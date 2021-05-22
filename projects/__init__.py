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

from flask import Flask, render_template
from flask_restful import Api

from projects.common import constants
from projects.resources.bp_user import bp


# db = SQLAlchemy()
# cors = CORS()


def create_app(config_name=None):
    # TODO 之後導入系統環境 加載配置
    if config_name is None:
        # config_name = os.getenv("FLASK_CONFIG", "dev")
        config_name = "dev"

    app = Flask(__name__)
    # 暫定預設配置 => flask\app.py
    # app.config.from_object(config_choice.get(config_name))

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


def register_logging(app: Flask):
    """ Set logging """
    fmt = "%(asctime)s - %(levelname)s - %(pathname)s[line:%(lineno)d]: %(message)s"
    # Set basic functions to loggin
    logging.basicConfig(level=logging.DEBUG, format=fmt)

    # Logger name
    # app.logger.name = "init_app"
    formatter = logging.Formatter(fmt)
    # Generate log day by day
    file_handler = TimedRotatingFileHandler(
        filename=((str(Path(Path(__file__).resolve().parents[1])) + constants.LOG_PATH) % datetime.now().strftime("%Y_%m_%d")),
        when="D",
        backupCount=30,
        encoding="utf-8")
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
    app.logger.info(f"Init projects log completely at {app.logger}")


def register_extensions(app: Flask):
    from projects.common.db import db_sqlalchemy
    from projects.common.ma import ma_marshmallow
    from projects.common.middleware import MiddleWare

    # Set WSGI's middleware
    app.wsgi_app = MiddleWare(app.wsgi_app)

    # Init database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db_sqlalchemy.init_app(app)

    # Init schema
    ma_marshmallow.init_app(app)

    # 初始化跨域模塊
    # cors.init_app(app)


def register_api(app: Flask):
    """ Set resources and rout """
    from projects.resources.re_hello_world import PrintHelloWorld
    from projects.resources.re_user import User, Users

    # The main entry point for the application
    api = Api(app)

    # Ex: Bind User to rout /print_hello_world/
    api.add_resource(PrintHelloWorld, '/print_hello_world/')
    api.add_resource(User, '/user/<string:name>')
    api.add_resource(Users, '/users/')

    # You can insert args into resources
    # api.add_resource(Users, '/users/', resource_class_args={app.logger})

    # TODO more useful with routing????
    # app.register_blueprint(index)
    # app.register_blueprint(admin)
    app.register_blueprint(bp)

    # 觀看有多少log存在於logging中 => 寫入file的log名稱為"projects"
    # loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    # for item in loggers:
    #     app.logger.debug(f"name: {item}, address: {hex(id(item))}")


def register_errors(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400


def register_commands(app: Flask):
    pass


def register_shell_context(app: Flask):
    pass


def register_template_context(app: Flask):
    pass
