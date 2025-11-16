from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import User
from app.extensions import db


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True
