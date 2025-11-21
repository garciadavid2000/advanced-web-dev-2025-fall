from flask import redirect, request
from app.controllers import auth_bp
from app.services.auth_service import AuthService
from config import oauth
from app.utils.session_manager import create_session, clear_session


@auth_bp.route('/login')
def login():
    google = oauth.create_client("google")
    return AuthService.get_google_login_url(google)


@auth_bp.route("/callback")
def google_callback():
    google = oauth.create_client("google")
    user = AuthService.handle_google_callback(google)
    create_session(user)
    return redirect("dashboard")


@auth_bp.route("/logout")
def logout():
    clear_session()
    return {"message": "Logged out"}
 