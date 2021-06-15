""" __init__.py
改變創建app實例的方式,不之間創建app,而是通過create_app函數里面創建,
再返回app對象,這樣的好處就是調用的時候才創建,想創建多少就調用多少,
而且每次調用都能應用不同的配置參數,這裡面這個create_app()就是應用的工廠方法!
在工廠方法裡面我們分別加載了配置擴展和藍圖
"""

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
from projects.routes.blueprints.bp_dailystock import dailystock_bp
from projects.routes.blueprints.bp_user import user_bp


# database = SQLAlchemy()
# cors = CORS()


def create_app(config_name=None):
    """ Start initialize the application """
    # TODO 之後導入系統環境 加載配置
    if config_name is None:
        # config_name = os.getenv("FLASK_CONFIG", "dev")
        config_name = 'dev'

    app = Flask(__name__)
    # 暫定預設配置 => flask\app.py
    # app.config.from_object(config_choice.get(config_name))

    # 加載Swagger
    register_swagger(app)
    # 加載日誌處理器
    register_logging(app)
    # 註冊擴展
    register_extensions(app)
    # 註冊API或者藍圖
    register_api(app)
    # 註冊錯誤處理
    register_errors(app)
    # 註冊click或script命令
    register_commands(app)
    # 註冊shell上下文
    register_shell_context(app)
    # 註冊模板上下文
    register_template_context(app)

    return app


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
        filename=((str(Path(Path(__file__).resolve().parents[0])) + constants.LOG_PATH) % datetime.now().strftime('%Y_%m_%d')),
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
    db_init.init_database(app, Databases.ORACLE_CLOUD)
    db_sqlalchemy.init_app(app)

    # Set schema
    ma_marshmallow.init_app(app)

    # 初始化跨域模塊
    # cors.init_app(app)

    app.logger.info(f'Register extensions completely')


def register_api(app: Flask):
    """ Set routes(routes and blueprints) """
    from projects.routes.resources.re_hello_world import PrintHelloWorld
    from projects.routes.resources.re_user import User, Users

    # The main entry point for the application
    api = Api(app)

    # Ex: Bind User to rout /print_hello_world/
    api.add_resource(PrintHelloWorld, '/print_hello_world/')
    api.add_resource(User, '/user/<string:name>')
    api.add_resource(Users, '/users/')

    # You can insert args into routes
    # api.add_resource(Users, '/users/', resource_class_args={app.logger})

    # TODO more useful with routing????
    # app.register_blueprint(index)
    # app.register_blueprint(admin)
    app.register_blueprint(blueprint=user_bp)
    app.register_blueprint(blueprint=dailystock_bp)

    # 觀看有多少log存在於logging中 => 寫入file的log名稱為'projects'
    # loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    # for item in loggers:
    #     app.logger.debug(f'name: {item}, address: {hex(id(item))}')

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
