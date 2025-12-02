from flask import session
from app.models import User

def create_session(user):
    session["user_id"] = user.id

def clear_session():
    session.pop("user_id", None)

def get_current_user():
    """Get the current authenticated user from session"""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)