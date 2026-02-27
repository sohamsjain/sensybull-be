from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timezone
import sqlalchemy as sa
from app import db
from app.models import Ticker
from app.models.user import User
from app.utils.schemas import TickerSchema
from app.services.alpaca import alpaca_client

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
# BATCH SNAPSHOTS (latest prices for multiple tickers)
# -----------------------
@tickers_bp.route('/snapshots', methods=['GET'])
@jwt_required()
def get_batch_snapshots():
    """Get latest prices for multiple tickers (comma-separated symbols param)"""
    symbols_param = request.args.get('symbols', '')
    if not symbols_param:
        return jsonify({'error': 'symbols parameter is required'}), 400

    symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
    if len(symbols) > 50:
        return jsonify({'error': 'Maximum 50 symbols per request'}), 400

    snapshots = alpaca_client.get_snapshots(symbols)

    prices = {}
    for sym, snap in snapshots.items():
        trade_price = snap.get('latestTrade', {}).get('p', 0)
        prev_close = snap.get('prevDailyBar', {}).get('c', 0)
        prices[sym] = {
            'price': trade_price,
            'prev_close': prev_close,
            'change_percent': (
                round(((trade_price - prev_close) / prev_close) * 100, 2)
                if prev_close > 0 else 0
            ),
        }

        # Opportunistic DB update
        if trade_price > 0:
            ticker = Ticker.query.filter_by(symbol=sym).first()
            if ticker:
                ticker.last_price = trade_price
                ticker.last_updated = datetime.now(timezone.utc)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({'prices': prices})


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
# GET STOCK SNAPSHOT (latest price, quote, daily bar)
# -----------------------
@tickers_bp.route('/<ticker_symbol>/snapshot', methods=['GET'])
@jwt_required()
def get_ticker_snapshot(ticker_symbol):
    """Get latest market data snapshot for a ticker from Alpaca"""
    symbol = ticker_symbol.upper()

    ticker = Ticker.query.filter_by(symbol=symbol).first_or_404()

    snapshot = alpaca_client.get_snapshot(symbol)
    if snapshot is None:
        return jsonify({'error': 'Failed to fetch market data'}), 502

    latest_trade = snapshot.get('latestTrade', {})
    trade_price = latest_trade.get('p', 0)

    # Opportunistic DB update
    if trade_price > 0:
        ticker.last_price = trade_price
        ticker.last_updated = datetime.now(timezone.utc)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    latest_quote = snapshot.get('latestQuote', {})
    daily_bar = snapshot.get('dailyBar', {})
    prev_daily_bar = snapshot.get('prevDailyBar', {})

    return jsonify({
        'symbol': symbol,
        'price': trade_price,
        'bid': latest_quote.get('bp', 0),
        'ask': latest_quote.get('ap', 0),
        'open': daily_bar.get('o', 0),
        'high': daily_bar.get('h', 0),
        'low': daily_bar.get('l', 0),
        'close': daily_bar.get('c', 0),
        'volume': daily_bar.get('v', 0),
        'prev_close': prev_daily_bar.get('c', 0),
    })


# -----------------------
# GET STOCK BARS (historical price data for charts)
# -----------------------
@tickers_bp.route('/<ticker_symbol>/bars', methods=['GET'])
@jwt_required()
def get_ticker_bars(ticker_symbol):
    """Get historical price bars for charting"""
    symbol = ticker_symbol.upper()

    Ticker.query.filter_by(symbol=symbol).first_or_404()

    timeframe = request.args.get('timeframe', '1Day')
    start = request.args.get('start')
    end = request.args.get('end')

    valid_timeframes = ['1Min', '5Min', '15Min', '1Hour', '1Day']
    if timeframe not in valid_timeframes:
        return jsonify({'error': f'Invalid timeframe. Must be one of: {valid_timeframes}'}), 400

    bars = alpaca_client.get_bars(symbol, timeframe=timeframe,
                                  start=start, end=end)

    price_points = []
    for bar in bars:
        bar_time = bar.get('t', '')
        try:
            dt = datetime.fromisoformat(bar_time.replace('Z', '+00:00'))
            ts = int(dt.timestamp())
        except (ValueError, AttributeError):
            continue

        price_points.append({
            'timestamp': ts,
            'price': bar.get('c', 0),
            'open': bar.get('o', 0),
            'high': bar.get('h', 0),
            'low': bar.get('l', 0),
            'volume': bar.get('v', 0),
        })

    return jsonify({
        'symbol': symbol,
        'timeframe': timeframe,
        'bars': price_points,
    })


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
