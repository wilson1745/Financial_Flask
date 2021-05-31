import logging

from sqlalchemy import *

from projects.common import constants
from projects.common.db import db_sqlalchemy
from projects.common.interceptor import interceptor

log = logging.getLogger(constants.LOG_PROJECTS)


class UserModel(db_sqlalchemy.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(120))

    def __init__(self, name, email, password):
        # self.id = None
        self.name = name
        self.email = email
        self.password = password

    def add_user(self):
        db_sqlalchemy.session.add(self)
        db_sqlalchemy.session.commit()

    def update_user(self):
        db_sqlalchemy.session.commit()

    @classmethod
    @interceptor
    def get_user(cls, name):
        log.debug(f"get_user name: {name}")
        return cls.query.filter_by(name=name).first()

    def delete_user(self):
        db_sqlalchemy.session.delete(self)
        db_sqlalchemy.session.commit()

    @classmethod
    def get_all_user(cls):
        return cls.query.all()
