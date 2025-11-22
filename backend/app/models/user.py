from app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255),)
    google_id = google_id = db.Column(db.String(255), unique=True, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now()
    )

    # relationships
    tasks = db.relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # def __repr__(self):
    #     return f"<User id={self.id} email={self.email!r}>"
