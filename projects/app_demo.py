""" This file contains your app and routes """
import logging

from flask import Flask
from flask_restful import Api

from projects.common.middleware import MiddleWare
from projects.resources.re_hello_world import PrintHelloWorld
from projects.resources.re_user import User, Users

APP = Flask(__name__)


def createApp():
    # global APP
    logging.basicConfig(level=logging.DEBUG)
    APP.logger.name = 'root_app'

    api = Api(APP)

    """ 使用WSGI的middleware """
    APP.wsgi_app = MiddleWare(APP.wsgi_app)

    """ 設定資料庫 """
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////resources/user.db'
    APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
    APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 把User綁定至url/user/
    api.add_resource(User, '/user/<string:name>')
    api.add_resource(Users, '/users/')
    api.add_resource(PrintHelloWorld, '/print_hello_world/')


if __name__ == '__main__':
    from projects.common.db import db_sqlalchemy
    from projects.common.ma import ma_marshmallow

    # with app.app_context():
    #     """ 使用WSGI的middleware """
    #     app.wsgi_app = middleware(app.wsgi_app)

    createApp()

    # global APP
    db_sqlalchemy.init_app(APP)
    ma_marshmallow.init_app(APP)

    """ debug=True => Detected change """
    APP.run(debug=True)
