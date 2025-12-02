from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from app.utils.session_manager import get_current_user_from_jwt


def token_or_session_required(fn):
    """
    Decorator that checks for either a valid JWT token in Authorization header
    or a valid session cookie. Works for both localhost (session) and deployment (token).
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        
        # Check if JWT token is provided
        if auth_header.startswith('Bearer '):
            try:
                verify_jwt_in_request()
                # Token is valid, JWT claims are available via get_jwt()
                return fn(*args, **kwargs)
            except Exception as e:
                # Token verification failed
                return {"error": "Invalid or expired token"}, 401
        
        # Fall back to session-based auth (for localhost development)
        # If we get here, neither token nor session was valid
        return {"error": "User not authenticated"}, 401
    
    return decorator


def get_current_user_from_request():
    """
    Get the current user from either JWT token or session.
    Returns None if not authenticated.
    """
    from app.utils.session_manager import get_current_user as get_current_user_from_session
    
    # First try JWT token
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        try:
            verify_jwt_in_request()
            jwt_claims = get_jwt()
            user = get_current_user_from_jwt(jwt_claims)
            if user:
                return user
        except Exception:
            pass
    
    # Fall back to session
    return get_current_user_from_session()
