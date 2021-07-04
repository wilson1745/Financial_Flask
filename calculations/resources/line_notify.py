# -*- coding: UTF-8 -*-
import multiprocessing
import os
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

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.constants import CLOSE_PRICE, D, K, K_D, MARKET_DATE, POS, RSI, RSI_Y, STOCK_NAME, SYMBOL
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_line_notify import NotifyGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.logic import FunctionKD, FunctionMA, FunctionRSI
from calculations.repository import dailystock_repo


@interceptor
def sendMsg(msg: list, token=constants.TOKEN_SENSATIONAL):
    """ Sending message through Line client """
    try:
        log.debug(f"sendMsg msg: {msg}")

        headers = {
            # "Authorization": "Bearer " + constants.TOKEN_NOTIFY,
            "Authorization": "Bearer " + token,
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
    except requests.exceptions.ConnectionError as connError:
        # FIXME 觀察一陣子
        """
        如果遇到沒有發送訊息的話，使用[遞歸]重新進行，直到成功為止 (https://www.cnblogs.com/Neeo/articles/11520952.html#urlliberror)
        """
        log.warning(f"ConnectionError msg: {msg}")
        CoreException.show_error(connError, traceback.format_exc())
        time.sleep(10)
        # Send notify again
        sendMsg(msg)
    except Exception as ex:
        CoreException.show_error(ex, traceback.format_exc())
        time.sleep(10)
    finally:
        time.sleep(2)


# @interceptor
def genStringRow(row) -> str:
    """ 建立每隻股票的格式 """
    rowStr = ""
    rowStr += f"\n名稱：{row[STOCK_NAME]} ({row[SYMBOL]})"
    rowStr += f"\n日期：{DateUtils.strformat(row[MARKET_DATE], constants.YYYYMMDD, constants.YYYYMMDD_SLASH)}"
    rowStr += f"\n收盤價：{row[CLOSE_PRICE]}"
    rowStr += f"\nRSI(12)值：{row[RSI]}%"
    rowStr += f"\nRSI較昨日：{'↑' if row[RSI_Y] > 0 else '↓'}{row[RSI_Y]}%"
    rowStr += f"\nKD(9)值：{row[K]}%, {row[D]}%"
    rowStr += f"\nK-D：{'↑' if row[K_D] > 0 else '↓'}{row[K_D]}%"

    return rowStr


@interceptor
def sendNotify(stockDict: dict):
    """ 預處理股票格式並用送出Line Notify """
    # TODO pool = multiprocessing.Pool(4)
    # TODO out1, out2, out3 = zip(*pool.map(calc_stuff, range(0, 10 * offset, offset)))

    key: NotifyGroup
    for key in stockDict:
        default = f"{DateUtils.default_msg(constants.YYYYMMDD_SLASH)}{key.getValue()}"
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
    FunctionRSI.GenRSI(data)
    FunctionKD.GenKD(data)
    stock = FunctionMA.GetCross(data, 5, 15)

    if not stock.empty:
        # Yesterday's RSI
        stock[RSI_Y] = (stock.iloc[-1][RSI] - stock.iloc[-2][RSI]).round(2)
        # KD Cross
        stock[K_D] = (stock.iloc[-1][K] - stock.iloc[-1][D]).round(2)
        # 取得當天含有RSI和KD值的最後一筆資料
        row: _iLocIndexer = stock.iloc[-1].copy()

        # Pandas SettingwithCopy 警告解决方案 (https://zhuanlan.zhihu.com/p/41202576)
        # pd.set_option('mode.chained_assignment', None)
        # row_pre: _iLocIndexer = stock.iloc[-2].copy()
        # row['RSI_Y'] = (row[RSI] - row_pre[RSI]).round(2)

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
                    """ Riley's stocks (from line_notify.py) """
                    for row in results.get():
                        if (row[RSI]) >= 70:
                            # 趕快賣的股票
                            stockDict[NotifyGroup.SELL].append(row)
                        elif row[RSI] <= 30:
                            # 好可憐的股票
                            stockDict[NotifyGroup.BAD].append(row)
                        else:
                            if row[RSI] >= 50 and row[POS] > 0:
                                # 進場做多
                                stockDict[NotifyGroup.LONG].append(row)
                            elif row[RSI] < 50 and row[POS] < 0:
                                # 進場做空
                                stockDict[NotifyGroup.SHORT].append(row)
                            else:
                                # 徘徊不定的股票
                                stockDict[NotifyGroup.NORMAL].append(row)
                else:
                    """ Portential stocks (from potential_stock.py) """
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
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)

    try:
        stocks = constants.RILEY_STOCKS
        log.debug(f"Symbols: {stocks}")
        arrangeNotify(stocks, NotifyGroup.getLineGroup())
        sendMsg([ms, constants.SUCCESS % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        sendMsg([ms, constants.FAIL % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
