import os
from authlib.integrations.flask_client import OAuth


class Config:
    """Base configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///streaks.db'
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    GOOGLE_CLIENT_ID = 'test-client-id'
    GOOGLE_CLIENT_SECRET = 'test-client-secret'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Handle Railway's DATABASE_URL which uses mysql:// but we need mysql+mysqlconnector://
    uri = os.environ.get('DATABASE_URL') or os.environ.get('DEV_DATABASE_URL')
    if uri and uri.startswith('mysql://'):
        uri = uri.replace('mysql://', 'mysql+mysqlconnector://', 1)
    SQLALCHEMY_DATABASE_URI = uri
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
