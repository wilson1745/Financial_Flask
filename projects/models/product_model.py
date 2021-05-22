from datetime import datetime

from projects.common.db import db_sqlalchemy


class Product(db_sqlalchemy.Model):
    __tablename__ = 'product'
    pid = db_sqlalchemy.Column(db_sqlalchemy.Integer, primary_key=True)
    name = db_sqlalchemy.Column(
        db_sqlalchemy.String(30), unique=True, nullable=False)
    price = db_sqlalchemy.Column(db_sqlalchemy.Integer, nullable=False)
    img = db_sqlalchemy.Column(
        db_sqlalchemy.String(100), unique=True, nullable=False)
    description = db_sqlalchemy.Column(
        db_sqlalchemy.String(255), nullable=False)
    state = db_sqlalchemy.Column(
        db_sqlalchemy.String(10), nullable=False)
    insert_time = db_sqlalchemy.Column(db_sqlalchemy.DateTime, default=datetime.now)
    update_time = db_sqlalchemy.Column(
        db_sqlalchemy.DateTime, onupdate=datetime.now, default=datetime.now)

    def __init__(self, name, price, img, description, state):
        self.name = name
        self.price = price
        self.img = img
        self.description = description
        self.state = state
