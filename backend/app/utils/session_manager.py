from flask import session

def create_session(user):
    session["user_id"] = user.id

def clear_session():
    session.pop("user_id", None)