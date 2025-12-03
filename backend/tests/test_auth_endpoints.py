import pytest
from unittest.mock import patch, MagicMock
from app.models.user import User

class TestAuthEndpoints:
    """Tests for auth controller endpoints."""

    # =====================
    # GET /login
    # =====================

    @patch('app.controllers.auth_controller.oauth.create_client')
    @patch('app.controllers.auth_controller.AuthService.get_google_login_url')
    def test_login(self, mock_get_url, mock_create_client, client):
        """Test login redirect."""
        mock_get_url.return_value = 'https://accounts.google.com/o/oauth2/auth'
        
        response = client.get('/auth/login')
        
        assert response.status_code == 200
        assert response.data.decode('utf-8') == 'https://accounts.google.com/o/oauth2/auth'
        mock_create_client.assert_called_with('google')

    # =====================
    # GET /callback
    # =====================

    @patch('app.controllers.auth_controller.oauth.create_client')
    @patch('app.controllers.auth_controller.AuthService.handle_google_callback')
    @patch('app.controllers.auth_controller.create_session')
    def test_google_callback(self, mock_create_session, mock_handle_callback, mock_create_client, client):
        """Test google callback handling."""
        mock_user = MagicMock(spec=User)
        mock_handle_callback.return_value = mock_user
        
        response = client.get('/auth/callback')
        
        assert response.status_code == 302  # Redirect to frontend
        mock_create_client.assert_called_with('google')
        mock_handle_callback.assert_called()
        mock_create_session.assert_called_with(mock_user)

    # =====================
    # GET /logout
    # =====================

    @patch('app.controllers.auth_controller.clear_session')
    def test_logout(self, mock_clear_session, client):
        """Test logout."""
        response = client.get('/auth/logout')
        
        assert response.status_code == 200
        assert response.get_json() == {"message": "Logged out"}
        mock_clear_session.assert_called_once()

    # =====================
    # POST /calendar/export
    # =====================

    @patch('app.controllers.auth_controller.TaskService.get_user_tasks')
    @patch('app.controllers.auth_controller.CalendarService.export_all_tasks_to_calendar')
    def test_calendar_export(self, mock_export, mock_get_tasks, authenticated_client, test_user):
        """Test calendar export success."""
        mock_get_tasks.return_value = {'2023-10-27': []}
        mock_export.return_value = {
            'success': 5,
            'deleted': 2,
            'failed': 0,
            'errors': [],
            'event_ids': []
        }
        
        response = authenticated_client.post('/auth/calendar/export')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == 5
        assert data['deleted'] == 2
        
        mock_get_tasks.assert_called_with(test_user['id'])
        # We can't easily assert the user object passed to export_all_tasks_to_calendar 
        # because it's fetched inside the view, but we verify the call happened.
        mock_export.assert_called()

    def test_calendar_export_unauthenticated(self, client):
        """Test calendar export without authentication."""
        response = client.post('/auth/calendar/export')
        
        assert response.status_code == 401

    @patch('app.controllers.auth_controller.TaskService.get_user_tasks')
    def test_calendar_export_no_tasks(self, mock_get_tasks, authenticated_client, test_user):
        """Test calendar export with no tasks."""
        mock_get_tasks.return_value = {}
        
        response = authenticated_client.post('/auth/calendar/export')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == "No tasks to export"

    @patch('app.controllers.auth_controller.TaskService.get_user_tasks')
    @patch('app.controllers.auth_controller.CalendarService.export_all_tasks_to_calendar')
    def test_calendar_export_error(self, mock_export, mock_get_tasks, authenticated_client, test_user):
        """Test calendar export handling exceptions."""
        mock_get_tasks.return_value = {'2023-10-27': []}
        mock_export.side_effect = ValueError("Calendar API Error")
        
        response = authenticated_client.post('/auth/calendar/export')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['error'] == "Calendar API Error"
