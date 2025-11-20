from flask import Flask
from app.extensions import db
from app.controllers import task_bp, user_bp
from sqlalchemy import event
from sqlalchemy.engine import Engine


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///streaks.db"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Enable foreign key support for SQLite
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
