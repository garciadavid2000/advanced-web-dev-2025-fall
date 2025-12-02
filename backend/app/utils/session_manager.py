from flask import session
from flask_jwt_extended import create_access_token
from app.models import User


def create_session(user):
    """Create a session for localhost development"""
    session["user_id"] = user.id


def clear_session():
    """Clear the session for localhost development"""
    session.pop("user_id", None)


def get_current_user():
    """Get the current authenticated user from session"""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def create_access_token_for_user(user):
    """Create a JWT access token for a user for deployment scenarios"""
    identity = {"user_id": user.id, "email": user.email}
    token = create_access_token(identity=identity)
    return token


def get_user_id_from_token(claims):
    """Extract user ID from JWT token claims"""
    if isinstance(claims, dict) and "user_id" in claims:
        return claims["user_id"]
    return None


def get_current_user_from_jwt(jwt_claims):
    """Get user from JWT token claims"""
    user_id = get_user_id_from_token(jwt_claims)
    if not user_id:
        return None
    return User.query.get(user_id)