import multiprocessing
import socket
import sys
import time
import traceback
from datetime import datetime
# from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool
from urllib.error import URLError

import requests
from pandas.core.indexing import _iLocIndexer
from requests import HTTPError

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_line_notify import NotifyGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.logic import FunctionKD, FunctionRSI
from calculations.repository import dailystock_repo


@interceptor
def sendMsg(msg: list):
    """ Sending message through Line client """
    try:
        headers = {
            "Authorization": "Bearer " + constants.TOKEN_NOTIFY,
            # "Authorization": "Bearer " + Constants.TOKEN_SENSATIONAL,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        params = {"message": ("\n".join(msg))}
        response = requests.post(constants.NOTIFY_LINK, headers=headers, params=params, timeout=60)

        """
        200 => success
        414 => message too long
        """
        # log.debug(f"Response status: {response.status_code}")
        log.debug(f"Response status: {response.status_code}")
        response.close()
    except Exception as ex:
        CoreException.show_error(ex, traceback.format_exc())
        time.sleep(10)
    finally:
        time.sleep(5)


# @interceptor
def genStringRow(row) -> str:
    """ 建立每隻股票的格式 """

    rowStr = ""
    rowStr += f"\n名稱: {row['stock_name']} ({row['symbol']})"
    rowStr += f"\n日期: {DateUtils.strformat(row['market_date'], constants.YYYYMMDD, constants.YYYYMMDD_SLASH)}"
    rowStr += f"\n收盤價: {row['close_price']}"
    rowStr += f"\nRSI值: {row['RSI']}%"
    rowStr += f"\nKD值: {row['K']}%, {row['D']}%"

    return rowStr


@interceptor
def sendNotify(stockDict: dict):
    """ 預處理股票格式並用送出Line Notify """
    # TODO pool = multiprocessing.Pool(4)
    # TODO out1, out2, out3 = zip(*pool.map(calc_stuff, range(0, 10 * offset, offset)))

    key: NotifyGroup
    for key in stockDict:
        default = f" ({DateUtils.today(constants.YYYYMMDD_SLASH)})\n{key.getValue()}"
        msg = [default]

        if len(stockDict[key]) > 0:
            for row in stockDict[key]:
                # extend => extract whatever types of element inside a list
                msg.extend([genStringRow(row)])

                # 1000 words limit with Line Notify
                if len(msg) % 10 == 0:
                    sendMsg(msg)
                    msg.clear()
                    msg.append(default)

            # Sending the rest data within 1000 words
            if len(msg) > 1:
                sendMsg(msg)
        else:
            msg.append("\n無資料...")
            sendMsg(msg)


@interceptor
def genNotifyData(symbol: str):
    log.debug(f"Start genNotifyStr: {symbol} at {datetime.now()} ")
    data = dailystock_repo.findBySymbol(symbol)
    FunctionRSI.GetDataRSI(data)
    stock = FunctionKD.GetDataKD(data)

    if not stock.empty:
        # 取得當天含有RSI和KD值的最後一筆資料
        row: _iLocIndexer = stock.iloc[-1]
        return row
    else:
        log.warning(constants.DATA_NOT_EXIST % symbol)
        return None


@interceptor
def arrangeNotify(symbols: list = None, stockDict: dict = None):
    """ Line Notify 主程式 """

    try:
        if symbols is None:
            log.warning("Warning => symbols: list = None")
        else:
            # Multiprocessing 設定處理程序數量
            # processPools = Pool(4)
            processPools = Pool(multiprocessing.cpu_count() - 1)
            results = processPools.map_async(func=genNotifyData,
                                             iterable=symbols,
                                             callback=CoreException.show,
                                             error_callback=CoreException.error)
            # results = processPools.starmap_async(genNotifyData,
            #                                      zip(symbols, repeat(pool)),
            #                                      callback=CoreException.show,
            #                                      error_callback=CoreException.show_error)

            # 包含Key資料的dictionary
            if len(results.get()) > 0:
                if not NotifyGroup.POTENTIAL in stockDict:
                    """ Riley's stock """
                    for row in results.get():
                        if (row["RSI"]) > 70:
                            stockDict[NotifyGroup.SELL].append(row)
                        elif row["RSI"] < 30:
                            stockDict[NotifyGroup.BAD].append(row)
                        else:
                            stockDict[NotifyGroup.NORMAL].append(row)
                else:
                    """ Portential stock (from potential_stock.py) """
                    for row in results.get():
                        stockDict[NotifyGroup.POTENTIAL].append(row)

                # 送出Line Notify
                sendNotify(stockDict)

            # 關閉process的pool並等待所有process結束
            processPools.close()
            processPools.join()

    except HTTPError as e_http:
        log.error(f"HTTP code error: {e_http.errno} {e_http.response}")
        raise e_http
    except URLError as e_url:
        if isinstance(e_url.reason, socket.timeout):
            log.error(f"socket timed out - URL {e_url}")
        raise e_url
    except Exception:
        raise


# ------------------- App Start -------------------
if __name__ == "__main__":
    now = time.time()
    try:
        stocks = constants.RILEY_STOCKS
        log.debug(f"Symbols: {stocks}")
        stockMainDict = {NotifyGroup.SELL: [], NotifyGroup.NORMAL: [], NotifyGroup.BAD: []}
        arrangeNotify(stocks, stockMainDict)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
