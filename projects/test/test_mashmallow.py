from datetime import datetime

from flask_marshmallow import Schema
from marshmallow import fields, pprint
from sqlalchemy import Column, String


class UserModel(object):
    __tablename__ = 'users'
    name = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)

    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.created_at = datetime.now()


class UserSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    created_at = fields.DateTime()


user = UserModel(name="Monty", email="monty@python.org")
schema = UserSchema()
result = schema.dump(user)
print(result)

json_result = schema.dumps(user)
print(json_result)
