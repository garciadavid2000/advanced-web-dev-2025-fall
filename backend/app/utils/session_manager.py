from flask import session

def create_session(user):
    session["user"] = user

def clear_session():
    session.pop("user", None)