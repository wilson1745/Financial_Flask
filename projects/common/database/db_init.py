import os
import platform

import cx_Oracle
from flask import Flask

from projects.common import constants
from projects.common.enums.enum_db import Databases


def init_database(app: Flask, db_name: Databases):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 對資料庫的任何操作，都會在 console 顯示
    app.config['SQLALCHEMY_ECHO'] = True

    if db_name == Databases.ORACLE_CLOUD:
        system_os = platform.system()

        if system_os == 'Windows':
            """ Using global path variable """
            os.environ.get('TNS_ADMIN')

            """ Using client directly """
        elif system_os == 'Darwin' or system_os == 'Linux':
            cx_Oracle.init_oracle_client(lib_dir=constants.LIB_DIR, config_dir=constants.CONFIG_DIR)
        else:
            raise Exception(f'Unknown system: {system_os}')

        # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user_name:password@IP:3306/db_name'
        app.config['SQLALCHEMY_DATABASE_URI'] = f"oracle+cx_oracle://" \
                                                f"{os.environ.get('ORACLE_ADW_USER')}:" \
                                                f"{os.environ.get('ORACLE_ADW_PASS')}" \
                                                f"@financialdb_high "
        # v2.4 開始新增 SQLALCHEMY_ENGINE_OPTIONS
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 90,
            'pool_timeout': 900,
            'pool_size': 5,
            # 暫時額外再新增多少的連線數
            'max_overflow': 3,
        }
    elif db_name == Databases.USER:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
