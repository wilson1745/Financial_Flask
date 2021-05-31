""" This file contains your app, routes and blueprints """

import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from flasgger import Swagger
from flask import Flask, render_template
from flask_restful import Api

from projects.common import constants
from projects.common.database import db_init
from projects.common.enums.enum_db import Databases
from projects.resources.bp_dailystock import dailystock_bp
from projects.resources.bp_user import user_bp


def register_swagger(app):
    """ Set swagger """
    app.config['SWAGGER'] = {
        'title': 'My API',
        'description': 'My API',
        'version': '1.0.2',
        'termsOfService': '',
        'hide_top_bar': False
    }
    # http://localhost:5000/apidocs/
    swagger = Swagger(app)


def register_logging(app: Flask):
    """ Set logging """
    fmt = '%(asctime)s - %(levelname)s - %(pathname)s[line:%(lineno)d]: %(message)s'
    # Set basic functions to loggin
    logging.basicConfig(level=logging.DEBUG, format=fmt)

    # Logger name
    # app.logger.name = 'init_app'
    formatter = logging.Formatter(fmt)
    # Generate log day by day
    file_handler = TimedRotatingFileHandler(
        filename=((str(Path(Path(__file__).resolve().parents[1])) + constants.LOG_PATH) % datetime.now().strftime('%Y_%m_%d')),
        when='D',
        backupCount=30,
        encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # TODO 之後導入系統環境
    # if not app.debug:
    #     app.logger.addHandler(file_hanlder)
    app.logger.addHandler(file_handler)

    # Let MiddleWare's werkzeug being writed into log
    logging.getLogger('werkzeug').setLevel(logging.DEBUG)
    logging.getLogger('werkzeug').addHandler(file_handler)

    # Test if log has run successfully
    app.logger.info(f'Init projects log completely at {app.logger}')


def register_extensions(app: Flask):
    """ Set extensions """
    from projects.common.db import db_sqlalchemy
    from projects.common.ma import ma_marshmallow
    from projects.common.middleware import MiddleWare

    # Set WSGI's middleware
    app.wsgi_app = MiddleWare(app.wsgi_app)

    # Set database
    db_init.init_database(app, Databases.USER)

    db_sqlalchemy.init_app(app)

    # Set schema
    ma_marshmallow.init_app(app)

    # 初始化跨域模塊
    # cors.init_app(app)

    app.logger.info(f'Register extensions completely')


def register_api(app: Flask):
    """ Set resources(routes and blueprints) """
    from projects.resources.re_hello_world import PrintHelloWorld
    from projects.resources.re_user import User, Users

    # The main entry point for the application
    api = Api(app)

    # Ex: Bind User to rout /print_hello_world/
    # Resources
    api.add_resource(PrintHelloWorld, '/print_hello_world/')
    api.add_resource(User, '/user/<string:name>')
    api.add_resource(Users, '/users/')

    # Blueprints
    app.register_blueprint(blueprint=user_bp)

    app.logger.info(f'Register api completely')


def register_errors(app: Flask):
    """ Set errors """

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400


def register_commands(app: Flask):
    """ Set commands """
    pass


def register_shell_context(app: Flask):
    """ Set shell context """
    pass


def register_template_context(app: Flask):
    """ Set template context """
    pass


def create_app(config_name=None):
    """ Start initialize the application """
    # TODO 之後導入系統環境 加載配置
    if config_name is None:
        # config_name = os.getenv("FLASK_CONFIG", "dev")
        config_name = "dev"

    app = Flask(__name__)
    # 暫定預設配置 => flask\app.py
    # app.config.from_object(config_choice.get(config_name))

    register_swagger(app)
    register_logging(app)
    register_extensions(app)
    register_api(app)
    register_errors(app)
    register_commands(app)
    register_shell_context(app)
    register_template_context(app)

    return app


if __name__ == '__main__':
    APP = create_app()

    """ debug=True => Detected change """
    APP.run(debug=True)
    # APP.run()
