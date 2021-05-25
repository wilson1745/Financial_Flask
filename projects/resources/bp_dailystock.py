# 第一個引數為藍圖名稱，隨便取
from flask import Blueprint

from projects.models.dailystock_model import DailyStockModel
from projects.models.schema.dailystock_schema import DailyStockSchema

# AttributeError: 'function' object has no attribute 'name' => 藍圖名字和系統名字出現重疊
dailystock_bp = Blueprint('dailystock', __name__)

dailystock_schema = DailyStockSchema(many=True)


@dailystock_bp.route('/dailystock_bp/<string:symbol>')
def symbol_get(symbol: str):
    try:
        data = DailyStockModel.find_by_symbol(symbol)
        result = dailystock_schema.dump(data)
        if not data:
            return {
                       'message': 'username not exist!'
                   }, 403

        return {
            'message': '',
            'result': result
        }
    except Exception as e:
        # CoreException.show_error(e, traceback.format_exc())
        return {
            "Exception message": str(e)
        }
