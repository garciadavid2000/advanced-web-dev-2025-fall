import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from datetime import datetime, timedelta


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client with clean state for each test."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(
            email="testuser@example.com",
            name="Test User",
            google_id="test-google-id-123"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return {'id': user_id, 'email': user.email}


@pytest.fixture
def authenticated_client(client, test_user):
    """Test client with authenticated session (user_id in session)."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_user['id']
    return client


@pytest.fixture
def second_test_user(app):
    """Create a second test user for testing user isolation."""
    with app.app_context():
        user = User(
            email="seconduser@example.com",
            name="Second Test User",
            google_id="test-google-id-456"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    return {'id': user_id, 'email': user.email}
