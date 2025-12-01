import os
from flask import Flask
from flask_cors import CORS
from app.extensions import db, oauth, init_oauth
from app.controllers import task_bp, user_bp, auth_bp
from config import config
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    """Application factory"""
    app = Flask(__name__)

    # Load configurations from the .env file
    load_dotenv()

    app.config.from_object(config[config_name])

    # Enable CORS with credentials support
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
    CORS(app, resources={r"/*": {"origins": [frontend_url, "http://localhost:3000", "http://localhost:5000"], "allow_headers": ["Content-Type"], "supports_credentials": True}})

    # Enable foreign key support for SQLite
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Initialize extensions
    db.init_app(app)
    init_oauth(app)
    
    # Register blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)

    # Create tables with retry logic
    with app.app_context():
        import time
        max_retries = 30
        for attempt in range(max_retries):
            try:
                db.create_all()
                break
            except Exception as e:
                if "already exists" in str(e):
                    app.logger.info("Tables already exist, skipping creation.")
                    break
                if attempt < max_retries - 1:
                    app.logger.warning(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(1)
                else:
                    app.logger.error(f"Failed to connect to database after {max_retries} attempts")
                    raise

    return app
