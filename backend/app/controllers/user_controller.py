from flask import request, jsonify, session
from app.controllers import user_bp
from app.services.user_service import UserService
from app.schemas import user_schema
from app.utils.jwt_required import get_current_user_from_request


@user_bp.route('/current', methods=['GET'])
def get_current_user():
    """Get the currently authenticated user from session or JWT token"""
    try:
        user = get_current_user_from_request()
        if not user:
            return {"error": "Not authenticated"}, 401
        
        return user_schema.dump(user), 200
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route('', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        
        if not email:
            return {"error": "email is required"}, 400
        
        user = UserService.create_user(email=email, name=name)
        return user_schema.dump(user), 201
    except ValueError as e:
        return {"error": str(e)}, 409
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route('<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a user by ID"""
    try:
        user = UserService.get_user(user_id)
        if user:
            return user_schema.dump(user), 200
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route('', methods=['GET'])
def get_all_users():
    """Get all users"""
    try:
        users = UserService.get_all_users()
        return {"users": [user_schema.dump(u) for u in users]}, 200
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route('<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user data"""
    try:
        data = request.get_json()
        user = UserService.update_user(user_id, **data)
        if user:
            return user_schema.dump(user), 200
        return {"error": "User not found"}, 404
    except ValueError as e:
        return {"error": str(e)}, 409
    except Exception as e:
        return {"error": str(e)}, 400


@user_bp.route('<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        if UserService.delete_user(user_id):
            return {"message": "User deleted successfully"}, 200
        return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 400
