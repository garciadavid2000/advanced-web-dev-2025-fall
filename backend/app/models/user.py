from app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255),)
    google_id = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now()
    )
    
    # OAuth token storage for calendar integration
    access_token = db.Column(db.Text, nullable=True)
    refresh_token = db.Column(db.Text, nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)

    # relationships
    tasks = db.relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def is_token_expired(self):
        """Check if the access token is expired"""
        if not self.token_expiry:
            return True
        return datetime.now() >= self.token_expiry

    # def __repr__(self):
    #     return f"<User id={self.id} email={self.email!r}>"
