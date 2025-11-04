from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlalchemy as sa
from app import db
from app.models import Ticker
from app.models.user import User
from app.utils.schemas import TickerSchema

tickers_bp = Blueprint('tickers', __name__)

ticker_schema = TickerSchema()
tickers_schema = TickerSchema(many=True)


# -----------------------
# SEARCH TICKERS
# -----------------------
@tickers_bp.route('/', methods=['GET'])
@jwt_required()
def search_tickers():
    """Search for tickers by symbol or name"""
    query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    tickers = []
    total = 0
    if query:
        tickers = Ticker.query.filter(
            sa.or_(
                Ticker.symbol.ilike(f'{query}%'),
                Ticker.name.ilike(f'%{query}%')
            )
        ).all()
        total = len(tickers)

    return jsonify({
        'tickers': tickers_schema.dump(tickers),
        'total': total,
        'page': page,
        'per_page': per_page
    })


# -----------------------
# GET SINGLE TICKER
# -----------------------
@tickers_bp.route('/<ticker_symbol>', methods=['GET'])
@jwt_required()
def get_ticker(ticker_symbol):
    """Get a single ticker by symbol"""
    ticker = Ticker.query.filter_by(symbol=ticker_symbol.upper()).first_or_404()
    return jsonify({'ticker': ticker_schema.dump(ticker)})


# -----------------------
# FOLLOW TICKER
# -----------------------
@tickers_bp.route('/<ticker_symbol>/follow', methods=['POST'])
@jwt_required()
def follow_ticker(ticker_symbol):
    """Follow a ticker"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Find the ticker
    ticker = Ticker.query.filter_by(symbol=ticker_symbol.upper()).first_or_404()

    # Check if already following
    if ticker in user.tickers:
        return jsonify({'message': 'Already following this ticker'}), 200

    # Add ticker to user's followed tickers
    user.tickers.append(ticker)

    try:
        db.session.commit()
        return jsonify({
            'message': f'Successfully followed {ticker.symbol}',
            'ticker': ticker_schema.dump(ticker)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to follow ticker', 'details': str(e)}), 500


# -----------------------
# UNFOLLOW TICKER
# -----------------------
@tickers_bp.route('/<ticker_symbol>/unfollow', methods=['DELETE'])
@jwt_required()
def unfollow_ticker(ticker_symbol):
    """Unfollow a ticker"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    # Find the ticker
    ticker = Ticker.query.filter_by(symbol=ticker_symbol.upper()).first_or_404()

    # Check if user is following
    if ticker not in user.tickers:
        return jsonify({'error': 'Not following this ticker'}), 404

    # Remove ticker from user's followed tickers
    user.tickers.remove(ticker)

    try:
        db.session.commit()
        return jsonify({
            'message': f'Successfully unfollowed {ticker.symbol}'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to unfollow ticker', 'details': str(e)}), 500


# -----------------------
# GET USER'S FOLLOWED TICKERS
# -----------------------
@tickers_bp.route('/following', methods=['GET'])
@jwt_required()
def get_followed_tickers():
    """Get all tickers the current user is following"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    return jsonify({
        'tickers': tickers_schema.dump(user.tickers),
        'total': len(user.tickers)
    })


# -----------------------
# CHECK IF FOLLOWING TICKER
# -----------------------
@tickers_bp.route('/<ticker_symbol>/is-following', methods=['GET'])
@jwt_required()
def is_following_ticker(ticker_symbol):
    """Check if the current user is following a specific ticker"""
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    ticker = Ticker.query.filter_by(symbol=ticker_symbol.upper()).first_or_404()

    is_following = ticker in user.tickers

    return jsonify({
        'ticker_symbol': ticker.symbol,
        'is_following': is_following
    })