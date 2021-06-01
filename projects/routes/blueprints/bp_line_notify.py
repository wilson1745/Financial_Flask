# AttributeError: 'function' object has no attribute 'name' => 藍圖名字和系統名字出現重疊
import logging
import multiprocessing
import socket
import time
import traceback
from datetime import datetime
# from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool
from urllib.error import URLError

from flask import Blueprint
from pandas.core.indexing import _iLocIndexer
from requests import HTTPError

from projects.common import constants
from projects.common.constants import LOG_PROJECTS
from projects.common.enums.enum_line_notify import NotifyGroup
from projects.common.exceptions.core_exception import CoreException
from projects.common.interceptor import interceptor
from projects.common.utils.data_frame_utils import DataFrameUtils
from projects.models.dailystock_model import DailyStockModel
from projects.models.schema.dailystock_schema import DailyStockSchema

log = logging.getLogger(LOG_PROJECTS)

line_notify_bp = Blueprint('dailystock', __name__)

dailystock_schema = DailyStockSchema(many=True)


@interceptor
def genNotifyData(symbol: str):
    # log.debug(f"Start genNotifyStr: {symbol} at {datetime.now()} ")
    # # data = dailystock_repo.findBySymbol(symbol)
    # # FunctionRSI.GetDataRSI(data)
    # # stock = FunctionKD.GetDataKD(data)
    #
    # data = DailyStockModel.find_by_symbol(symbol)
    # if not data:
    #     log.warning(f'{symbol} no data exist!')
    #     return
    # else:
    #     result = dailystock_schema.dump(data, many=True)
    #     df = DataFrameUtils.genDataFrame(result)
    #     FunctionRSI.GetDataRSI(data)
    #
    # if not stock.empty:
    #     # 取得當天含有RSI和KD值的最後一筆資料
    #     row: _iLocIndexer = stock.iloc[-1]
    #     return row
    # else:
    #     log.warning(constants.DATA_NOT_EXIST % symbol)
    #     return None
    pass


@interceptor
def arrangeNotify(symbols: list = None, stockDict: dict = None):
    # """ Line Notify 主程式 """
    #
    # try:
    #     if symbols is None:
    #         log.warning("Warning => symbols: list = None")
    #     else:
    #         # Multiprocessing 設定處理程序數量
    #         # processPools = Pool(4)
    #         processPools = Pool(multiprocessing.cpu_count() - 1)
    #         results = processPools.map_async(func=genNotifyData,
    #                                          iterable=symbols,
    #                                          callback=CoreException.show,
    #                                          error_callback=CoreException.error)
    #         # results = processPools.starmap_async(genNotifyData,
    #         #                                      zip(symbols, repeat(pool)),
    #         #                                      callback=CoreException.show,
    #         #                                      error_callback=CoreException.show_error)
    #
    #         # 包含Key資料的dictionary
    #         if len(results.get()) > 0:
    #             if not NotifyGroup.POTENTIAL in stockDict:
    #                 """ Riley's stock """
    #                 for row in results.get():
    #                     if (row["RSI"]) > 70:
    #                         stockDict[NotifyGroup.SELL].append(row)
    #                     elif row["RSI"] < 30:
    #                         stockDict[NotifyGroup.BAD].append(row)
    #                     else:
    #                         stockDict[NotifyGroup.NORMAL].append(row)
    #             else:
    #                 """ Portential stock (from potential_stock.py) """
    #                 for row in results.get():
    #                     stockDict[NotifyGroup.POTENTIAL].append(row)
    #
    #             # 送出Line Notify
    #             sendNotify(stockDict)
    #
    #         # 關閉process的pool並等待所有process結束
    #         processPools.close()
    #         processPools.join()
    #
    # except HTTPError as e_http:
    #     log.error(f"HTTP code error: {e_http.errno} {e_http.response}")
    #     raise e_http
    # except URLError as e_url:
    #     if isinstance(e_url.reason, socket.timeout):
    #         log.error(f"socket timed out - URL {e_url}")
    #     raise e_url
    # except Exception:
    #     raise
    pass


@line_notify_bp.route('/line_notify_bp/main')
def main():
    """ App Start """
    now = time.time()
    try:
        #     stocks = constants.RILEY_STOCKS
        #     log.debug(f"Symbols: {stocks}")
        #     stockMainDict = {NotifyGroup.SELL: [], NotifyGroup.NORMAL: [], NotifyGroup.BAD: []}
        #     arrangeNotify(stocks, stockMainDict)
        #
        #     data = DailyStockModel.find_by_symbol(symbol)
        #     if not data:
        #         return {
        #                    'message': 'username not exist!'
        #                }, 403
        #
        #     result = dailystock_schema.dump(data, many=True)
        #     return {
        #         'message': '',
        #         'result': result
        #     }
        return "OK"
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        return {
            'Exception message': str(e)
        }
