from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
import sqlalchemy as sa
from app.models import Ticker
from app.utils.schemas import TickerSchema

tickers_bp = Blueprint('tickers', __name__)

tickers_schema = TickerSchema(many=True)


# -----------------------
# SEARCH TICKERS
# -----------------------
@tickers_bp.route('/', methods=['GET'])
@jwt_required()
def search_tickers():
    query = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    tickers = []
    total = 0
    if query:
        tickers = Ticker.query.filter(sa.or_(Ticker.symbol.ilike(f'{query}%'), Ticker.name.ilike(f'%{query}%'))).all()
        total = len(tickers)

    return jsonify({
        'tickers': tickers_schema.dump(tickers),
        'total': total,
        'page': page,
        'per_page': per_page
    })
