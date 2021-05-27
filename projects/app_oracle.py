""" This file contains your app and routes """
import os
import platform

import cx_Oracle
import pandas as pd
from flasgger import Swagger, swag_from
from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from pandas import DataFrame

from projects.resources.bp_dailystock import dailystock_bp

HEADERS = ["market_date", "stock_name", "symbol", "deal_stock", "deal_price", "opening_price", "highest_price",
           "lowest_price", "close_price", "ups_and_downs", "volume", "createtime"]

db = SQLAlchemy()
ma = Marshmallow()

app = Flask(__name__)

app.config['SWAGGER'] = {
    "title": "My API",
    "description": "My API",
    "version": "1.0.2",
    "termsOfService": "",
    "hide_top_bar": False
}

# http://localhost:5000/apidocs/
swagger = Swagger(app)


def initOracle():
    system_os = platform.system()

    if system_os == "Windows":
        """ Using global path variable """
        os.environ.get("TNS_ADMIN")

        """ Using client directly """
    elif system_os == "Darwin" or system_os == "Linux":
        cx_Oracle.init_oracle_client(lib_dir="/Users/WilsonLo/Downloads/instantclient_19_8",
                                     config_dir="/Users/WilsonLo/oracle/Wallet_financialDB")
    else:
        raise Exception(f"Unknown system: {system_os}")

    username = os.environ.get("ORACLE_ADW_USER")
    password = os.environ.get("ORACLE_ADW_PASS")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://user_name:password@IP:3306/db_name"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"oracle+cx_oracle://{username}:{password}@financialdb_high"
    # v2.4 開始新增 SQLALCHEMY_ENGINE_OPTIONS
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 90,
        "pool_timeout": 900,
        "pool_size": 5,
        # 暫時額外再新增多少的連線數
        "max_overflow": 3,
    }
    # 對資料庫的任何操作，都會在 console 顯示
    app.config['SQLALCHEMY_ECHO'] = True


def genDataFrame(datas: list) -> DataFrame:
    """ Generate pandas dataframe """

    try:
        pd.set_option("display.width", 320)
        pd.set_option("display.max_columns", 20)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.unicode.ambiguous_as_wide", True)
        pd.set_option("display.unicode.east_asian_width", True)

        df = pd.DataFrame(datas)
        df.columns = HEADERS
        df.index = pd.to_datetime(df["market_date"])

        return df

    except Exception as e:
        print(str(e))


# @app.route('/')
# def index():
#     # sql_cmd = """
#     #     SELECT *
#     #     FROM DAILYSTOCK d WHERE d.SYMBOL = '2330' ORDER BY d.MARKET_DATE ASC
#     #     """
#     #
#     # query_data = db.engine.execute(sql_cmd)
#     # df = genDataFrame(query_data.fetchall())
#     # return df.to_json(orient='records', force_ascii=False)
#     return "Route OK!!!!!!!!!!!!!!!!!!!!!"


@app.route('/colorsssss/')
# @swag_from('index.yml')
def colorsssss(palette):
    # sql_cmd = """
    #     SELECT *
    #     FROM DAILYSTOCK d WHERE d.SYMBOL = '2330' ORDER BY d.MARKET_DATE ASC
    #     """
    #
    # query_data = db.engine.execute(sql_cmd)
    # df = genDataFrame(query_data.fetchall())
    # return df.to_json(orient='records', force_ascii=False)
    return "Route OK!!!!!!!!!!!!!!!!!!!!!"


# @app.route('/colors/<palette>/')
# def colors(palette):
#     """Example endpoint returning a list of colors by palette
#     This is using docstrings for specifications.
#     ---
#     parameters:
#       - name: palette
#         in: path
#         type: string
#         enum: ['all', 'rgb', 'cmyk']
#         required: true
#         default: all
#     definitions:
#       Palette:
#         type: object
#         properties:
#           palette_name:
#             type: array
#             items:
#               $ref: '#/definitions/Color'
#       Color:
#         type: string
#     responses:
#       200:
#         description: A list of colors (may be filtered by palette)
#         schema:
#           $ref: '#/definitions/Palette'
#         examples:
#           rgb: ['red', 'green', 'blue']
#     """
#     all_colors = {
#         'cmyk': ['cian', 'magenta', 'yellow', 'black'],
#         'rgb': ['red', 'green', 'blue']
#     }
#     if palette == 'all':
#         result = all_colors
#     else:
#         result = {palette: all_colors.get(palette)}
#
#     return jsonify(result)


if __name__ == '__main__':
    initOracle()

    db.init_app(app)
    ma.init_app(app)

    # The main entry point for the application
    api = Api(app)
    app.register_blueprint(blueprint=dailystock_bp)

    app.run(debug=True)
