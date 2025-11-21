from flask import Flask
from app.extensions import db
from app.controllers import task_bp, user_bp, auth_bp
from config import oauth, config
from sqlalchemy import event
from sqlalchemy.engine import Engine
from dotenv import load_dotenv


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)

    # Load configurations from the .env file
    load_dotenv()

    app.config.from_object(config[config_name])

    oauth.init_app(app)

    # Enable foreign key support for SQLite
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Initialize extensions
    db.init_app(app)

    # Setting up OAuth
    oauth.register(
        name="google",
        client_id=app.config["GOOGLE_CLIENT_ID"],
        client_secret=app.config["GOOGLE_CLIENT_SECRET"],
        access_token_url="https://oauth2.googleapis.com/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        api_base_url="https://www.googleapis.com/",
        client_kwargs={
            "scope": "openid email profile https://www.googleapis.com/auth/calendar"
        },
    )

    # Register blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
