import os
from flask import Flask, send_from_directory, send_file
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS
from app.extensions import db, oauth, init_oauth
from app.controllers import task_bp, user_bp, auth_bp
from config import config
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv


def create_app(config_name='development'):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    """Application factory"""
    app = Flask(__name__)

    # Load configurations from the .env file
    load_dotenv()

    app.config.from_object(config[config_name])

    print(app.config['SQLALCHEMY_DATABASE_URI'])

    # Apply ProxyFix to handle headers from Railway's load balancer
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Enable CORS only if running with separate frontend (for development)
    # In monolith/production, frontend and backend are on same origin, so CORS not needed
    if os.environ.get('SEPARATE_FRONTEND', 'false').lower() == 'true':
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        CORS(app, resources={r"/*": {"origins": [frontend_url, "http://localhost:3000"], "allow_headers": ["Content-Type"], "supports_credentials": True}})

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
    
    # Register API blueprints FIRST so they take priority over frontend catch-all routes
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    FRONTEND_DIR = os.path.join(BASE_DIR, '..', 'static', 'frontend')
    print(FRONTEND_DIR)

    # Serve frontend static assets and handle SPA routing
    @app.route('/')
    def index():
        """Serve the Next.js frontend index"""
        try:
            return send_from_directory(FRONTEND_DIR, 'index.html')
        except FileNotFoundError:
            return {'error': 'Frontend not built'}, 404

    @app.route('/<path:path>')
    def serve_frontend(path):
        """Serve static assets and fallback to index.html for SPA routing"""
        # Don't intercept actual API routes (they should be handled by blueprints above)
        # This is a safety check in case requests reach here
        if path.startswith('api/'):
            return {'error': 'Not found'}, 404
        
        # Serve static files (.js, .css, images, etc.)
        try:
            return send_from_directory(FRONTEND_DIR, path)
        except FileNotFoundError:
            # Fallback to index.html for client-side routing
            try:
                return send_from_directory(FRONTEND_DIR, 'index.html')
            except FileNotFoundError:
                return {'error': 'Frontend not found'}, 404

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
