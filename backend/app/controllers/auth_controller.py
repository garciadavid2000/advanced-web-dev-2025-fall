import os
from flask import redirect, request, jsonify
from app.controllers import auth_bp
from app.services.auth_service import AuthService
from app.services.calendar_service import CalendarService
from app.services.task_service import TaskService
from app.extensions import oauth
from app.utils.session_manager import create_session, clear_session, get_current_user


@auth_bp.route('/login')
def login():
    google = oauth.create_client("google")
    return AuthService.get_google_login_url(google)


@auth_bp.route("/callback")
def google_callback():
    google = oauth.create_client("google")
    user = AuthService.handle_google_callback(google)
    create_session(user)
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5000')
    return redirect(frontend_url)


@auth_bp.route("/logout")
def logout():
    clear_session()
    return {"message": "Logged out"}


@auth_bp.route("/calendar/export", methods=["POST"])
def export_to_calendar():
    """Export all user tasks to Google Calendar"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({"error": "User not authenticated"}), 401
        
        # Get user's tasks grouped by date
        tasks_by_date = TaskService.get_user_tasks(user.id)
        
        if not tasks_by_date:
            return jsonify({
                "message": "No tasks to export",
                "success": 0,
                "failed": 0
            }), 200
        
        # Sync to calendar (deletes old events, creates new ones)
        result = CalendarService.export_all_tasks_to_calendar(user, tasks_by_date)
        
        return jsonify({
            "message": f"Synced {result['success']} tasks to calendar (deleted {result['deleted']} old events)",
            "deleted": result['deleted'],
            "success": result['success'],
            "failed": result['failed'],
            "errors": result['errors'],
            "event_ids": result['event_ids']
        }), 200
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
