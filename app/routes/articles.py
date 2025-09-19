from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, or_, and_, func
from app import db
from app.models.article import Article
from app.models.ticker import Ticker
from app.models.user import User
from app.utils.schemas import ArticleSchema, ArticleCreateSchema
from app.utils.auth import admin_required
from datetime import datetime, timezone

articles_bp = Blueprint('articles', __name__)

article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
article_create_schema = ArticleCreateSchema()


# ---------------- CREATE ARTICLE ----------------
@articles_bp.route('/', methods=['POST'])
def create_article():
    """Create a new article - no authentication required for scraper"""
    try:
        data = article_create_schema.load(request.json)
    except ValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400

    # Check if article with this URL already exists
    existing_article = Article.query.filter_by(url=data['url']).first()
    if existing_article:
        return jsonify({'error': 'Article with this URL already exists'}), 409

    # Handle ticker associations
    ticker_symbols = data.pop('tickers', [])
    tickers = []
    if ticker_symbols:
        for symbol in ticker_symbols:
            ticker = Ticker.query.filter_by(symbol=symbol).first()
            if not ticker:
                continue
            tickers.append(ticker)

    article = Article(**data)
    article.tickers = tickers

    try:
        db.session.add(article)
        db.session.commit()

        return jsonify({
            'message': 'Article created successfully',
            'article': article_schema.dump(article)
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Article with this URL already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create article', 'details': str(e)}), 500


# ---------------- GET ALL ARTICLES ----------------
@articles_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_articles():
    """Get all articles with optional filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)  # Max 100 per page
    ticker_symbol = request.args.get('ticker', type=str)
    provider = request.args.get('provider', type=str)
    search = request.args.get('search', type=str)
    start_date = request.args.get('start_date', type=int)  # Unix timestamp
    end_date = request.args.get('end_date', type=int)  # Unix timestamp

    # Build query
    query = Article.query

    # Filter by ticker
    if ticker_symbol:
        query = query.join(Article.tickers).filter(Ticker.symbol == ticker_symbol.upper())

    # Filter by provider
    if provider:
        query = query.filter(Article.provider.ilike(f'%{provider}%'))

    # Search in title and summary
    if search:
        search_term = f'%{search}%'
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.summary.ilike(search_term)
            )
        )

    # Date range filters
    if start_date:
        query = query.filter(Article.timestamp >= start_date)
    if end_date:
        query = query.filter(Article.timestamp <= end_date)

    # Order by timestamp (newest first)
    query = query.order_by(desc(Article.timestamp))

    # Paginate
    articles = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'articles': articles_schema.dump(articles.items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': articles.total,
            'pages': articles.pages,
            'has_next': articles.has_next,
            'has_prev': articles.has_prev
        }
    })


# ---------------- GET SINGLE ARTICLE ----------------
@articles_bp.route('/<article_id>', methods=['GET'])
@jwt_required()
def get_article(article_id):
    """Get a single article by ID"""
    article = Article.query.get_or_404(article_id)
    return jsonify({'article': article_schema.dump(article)})


# ---------------- GET ARTICLES BY TICKER ----------------
@articles_bp.route('/ticker/<ticker_symbol>', methods=['GET'])
@jwt_required()
def get_articles_by_ticker(ticker_symbol):
    """Get all articles for a specific ticker"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    # Verify ticker exists
    ticker = Ticker.query.filter_by(symbol=ticker_symbol.upper()).first_or_404()

    # Get articles for this ticker
    articles = Article.query.join(Article.tickers) \
        .filter(Ticker.symbol == ticker_symbol.upper()) \
        .order_by(desc(Article.timestamp)) \
        .paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return jsonify({
        'ticker': ticker_symbol.upper(),
        'articles': articles_schema.dump(articles.items),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': articles.total,
            'pages': articles.pages,
            'has_next': articles.has_next,
            'has_prev': articles.has_prev
        }
    })