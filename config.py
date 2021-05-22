import os


class BaseConfig:
    # 基礎配置
    DEBUG = False
    HOST = "127.0.0.1"
    PORT = "5000"

    # 系統配置
    SECRET_KEY = os.getenv("SECRET_KEY", "set a secret key")
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

    # 數據庫配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(BaseConfig):
    # 基礎配置
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    HOST = "0.0.0.0"

    # 數據庫配置
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BaseConfig.PROJECT_ROOT, 'data-dev.db')


class TestingConfig(DevConfig):
    # 基礎配置
    TESTING = True
    WTF_CSTF_ENABLED = False

    # 數據庫配置
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProdConfig(BaseConfig):
    # 基礎配置
    DEBUG = False
    SQLALCHEMY_ECHO = False
    HOST = "0.0.0.0"
    PORT = "5000"

    # 數據庫配置
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BaseConfig.PROJECT_ROOT, 'data.db')


config_choice = {
    "default": BaseConfig,
    "dev": DevConfig,
    "test": TestingConfig,
    "prod": ProdConfig
}
