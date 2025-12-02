from datetime import datetime
from app.extensions import db
from app.models import User


class UserService:
    """Business logic for user operations"""

    # ----------------- THESE FUNCTIONS ARE TO BE OFFBOARDED -----------------

    @staticmethod
    def create_user(email, name=None):
        """Create a new user"""
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        user = User(email=email, name=name)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user(user_id):
        """Get a user by ID"""
        return db.session.get(User, user_id)

    @staticmethod
    def get_user_by_email(email):
        """Get a user by email"""
        return User.query.filter_by(email=email).first()
    
    # -----------------  -----------------
    
    @staticmethod
    def get_or_create_google_user(google_id, email, name):
        """
        Find user using google_id or email.
        If none exists, create a new user linked to Google.
        """
        print(google_id, email, name)
        user = None

        # Try finding by google_id first
        if google_id:
            user = User.query.filter_by(google_id=google_id).first()

        # If not found, try finding by email
        if not user:
            user = User.query.filter_by(email=email).first()

        if user:
            # Update fields if changed
            updated = False

            if not user.google_id:
                user.google_id = google_id
                updated = True

            user.last_login = datetime.now()
            updated = True

            if updated:
                db.session.commit()

            return user
        
        new_user = User(
            email=email,
            google_id=google_id,
            name=name
        )

        db.session.add(new_user)
        db.session.commit()
        return new_user


    @staticmethod
    def update_user(user_id, **kwargs):
        """Update user data"""
        user = db.session.get(User, user_id)
        if not user:
            return None
        
        # Only allow updating these fields
        allowed_fields = {'name', 'email'}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                # Check if email is already taken by another user
                if key == 'email' and value != user.email:
                    existing = User.query.filter_by(email=value).first()
                    if existing:
                        raise ValueError(f"Email {value} is already taken")
                setattr(user, key, value)
            else:
                raise Exception(f"Cannot update field: {key}")
        
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id):
        """Delete a user"""
        user = db.session.get(User, user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_all_users():
        """Get all users"""
        return User.query.all()

    @staticmethod
    def update_user_tokens(user):
        """Update OAuth tokens for a user (called after OAuth callback)"""
        db.session.merge(user)
        db.session.commit()
        return user
