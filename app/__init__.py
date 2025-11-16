from flask import Flask
from app.extensions import db
from app.controllers import task_bp


def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///streaks.db"
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(task_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
