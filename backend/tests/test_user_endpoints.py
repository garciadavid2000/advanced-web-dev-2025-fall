import pytest
from app.models.user import User
from app.extensions import db

class TestUserEndpoints:
    """Tests for user controller endpoints."""

    # =====================
    # GET /users/current
    # =====================

    def test_get_current_user(self, authenticated_client, test_user):
        """Test retrieving the currently authenticated user."""
        response = authenticated_client.get('/users/current')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == test_user['email']
        assert data['id'] == test_user['id']

    def test_get_current_user_unauthorized(self, client):
        """Test retrieving current user without authentication."""
        response = client.get('/users/current')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    # =====================
    # POST /users
    # =====================

    def test_create_user(self, client, app):
        """Test creating a new user."""
        response = client.post(
            '/users',
            json={
                'email': 'newuser@example.com',
                'name': 'New User'
            }
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['email'] == 'newuser@example.com'
        assert data['name'] == 'New User'
        
        with app.app_context():
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None

    def test_create_user_missing_email(self, client):
        """Test creating a user without email fails."""
        response = client.post(
            '/users',
            json={
                'name': 'No Email User'
            }
        )
        
        assert response.status_code == 400

    def test_create_user_duplicate_email(self, client, test_user):
        """Test creating a user with existing email fails."""
        response = client.post(
            '/users',
            json={
                'email': test_user['email'],
                'name': 'Duplicate User'
            }
        )
        
        assert response.status_code == 409

    # =====================
    # GET /users/<id>
    # =====================

    def test_get_user(self, client, test_user):
        """Test retrieving a specific user by ID."""
        response = client.get(f'/users/{test_user["id"]}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == test_user['email']

    def test_get_nonexistent_user(self, client):
        """Test retrieving a user that doesn't exist."""
        response = client.get('/users/99999')
        
        assert response.status_code == 404

    # =====================
    # GET /users
    # =====================

    def test_get_all_users(self, client, test_user, second_test_user):
        """Test retrieving all users."""
        response = client.get('/users')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert len(data['users']) >= 2
        
        emails = [u['email'] for u in data['users']]
        assert test_user['email'] in emails
        assert second_test_user['email'] in emails

    # =====================
    # PUT /users/<id>
    # =====================

    def test_update_user(self, client, test_user, app):
        """Test updating user details."""
        response = client.put(
            f'/users/{test_user["id"]}',
            json={
                'name': 'Updated Name'
            }
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Updated Name'
        
        with app.app_context():
            user = db.session.get(User, test_user['id'])
            assert user.name == 'Updated Name'

    def test_update_nonexistent_user(self, client):
        """Test updating a user that doesn't exist."""
        response = client.put(
            '/users/99999',
            json={'name': 'Ghost'}
        )
        
        assert response.status_code == 404

    # =====================
    # DELETE /users/<id>
    # =====================

    def test_delete_user(self, client, test_user, app):
        """Test deleting a user."""
        response = client.delete(f'/users/{test_user["id"]}')
        
        assert response.status_code == 200
        
        with app.app_context():
            user = db.session.get(User, test_user['id'])
            assert user is None

    def test_delete_nonexistent_user(self, client):
        """Test deleting a user that doesn't exist."""
        response = client.delete('/users/99999')
        
        assert response.status_code == 404
