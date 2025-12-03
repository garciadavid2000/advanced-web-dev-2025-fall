from functools import wraps
from flask import request, jsonify, g
from app.utils.session_manager import get_current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401
        # Store user in g for easy access if needed, though get_current_user does session lookup
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function
