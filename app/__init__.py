from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from sqlalchemy import event


db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    app.url_map.strict_slashes = False

    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:

        with app.app_context():
            @event.listens_for(db.engine, "connect")
            def enable_wal(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.close()

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.tickers import tickers_bp
    from app.routes.topics import topics_bp
    from app.routes.articles import articles_bp
    from app.routes.chat import chat_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(tickers_bp, url_prefix='/tickers')
    app.register_blueprint(topics_bp, url_prefix='/topics')
    app.register_blueprint(articles_bp, url_prefix='/articles')
    app.register_blueprint(chat_bp, url_prefix='/chat')

    # Error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    return app