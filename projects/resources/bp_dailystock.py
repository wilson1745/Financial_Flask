# 第一個引數為藍圖名稱，隨便取
import traceback

from flask import Blueprint

from projects.common.exceptions.core_exception import CoreException
from projects.common.utils.data_frame_utils import DataFrameUtils
from projects.models.dailystock_model import DailyStockModel
from projects.models.schema.dailystock_schema import DailyStockSchema

# AttributeError: 'function' object has no attribute 'name' => 藍圖名字和系統名字出現重疊
dailystock_bp = Blueprint('dailystock', __name__)

dailystock_schema = DailyStockSchema(many=True)


@dailystock_bp.route('/dailystock_bp/<string:symbol>')
def symbol_get(symbol: str):
    try:
        data = DailyStockModel.find_by_symbol(symbol)
        if not data:
            return {
                       'message': 'username not exist!'
                   }, 403

        result = dailystock_schema.dump(data, many=True)
        return {
            'message': '',
            'result': result
        }
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        return {
            'Exception message': str(e)
        }


@dailystock_bp.route('/dailystock_bp/symbol_get_df/<string:symbol>')
def symbol_get_df(symbol: str):
    try:
        data = DailyStockModel.find_by_symbol(symbol)
        if not data:
            return {
                       'message': 'username not exist!'
                   }, 403

        result = dailystock_schema.dump(data, many=True)
        df = DataFrameUtils.genDataFrame(result)
        return {
            'message': '',
            'result': df.to_json(orient='index', force_ascii=False)
        }
        # return df.to_json(orient='index', force_ascii=False)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        return {
            'Exception message': str(e)
        }

# @dailystock_bp.route('/dailystock_bp/raw_sql/')
# # @swag_from('index.yml')
# def colorsssss():
#     sql_cmd = """
#         SELECT *
#         FROM DAILYSTOCK d WHERE d.SYMBOL = '2330' ORDER BY d.MARKET_DATE ASC
#         """
#
#     query_data = db_sqlalchemy.engine.execute(sql_cmd)
#     df = DataFrameUtils.genDataFrame(query_data.fetchall())
#     return df.to_json(orient='index', force_ascii=False)


# @dailystock_bp.route('/colors/<palette>/')
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
