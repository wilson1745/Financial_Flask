# -*- coding: UTF-8 -*-
import multiprocessing
import os
import sys
import time
import traceback
from datetime import datetime
# from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool

import requests
from pandas import DataFrame
from pandas.core.indexing import _iLocIndexer

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.constants import CLOSE, D, K, K_D, MARKET_DATE, RSI, RSI_Y, SGNL_B, SGNL_S, STOCK_NAME, SYMBOL, UPS_AND_DOWNS, \
    UPS_AND_DOWNS_PCT
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_line_notify import NotifyGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.logic import FunctionBollingBand, FunctionKD, FunctionMA, FunctionRSI
from calculations.repository import dailystock_repo


def __msgArrow(value: float) -> str:
    sym = ''
    if value > 0:
        sym = '↑'
    elif value < 0:
        sym = '↓'
    return f"{sym}{value}"


# @interceptor
def __genStringRow(row) -> str:
    """ 建立每隻股票的格式 """
    rowStr = ""
    rowStr += f"\n名稱：{row[STOCK_NAME]} ({row[SYMBOL]})"
    rowStr += f"\n日期：{DateUtils.strformat(row[MARKET_DATE], constants.YYYYMMDD, constants.YYYYMMDD_SLASH)}"
    rowStr += f"\n收盤價：{row[CLOSE]}"
    rowStr += f"\nRSI(12)值：{row[RSI]}%"
    rowStr += f"\nRSI較昨日：{'↑' if row[RSI_Y] > 0 else '↓'}{row[RSI_Y]}%"
    rowStr += f"\nKD(9)值：{row[K]}%, {row[D]}%"
    rowStr += f"\nK-D：{'↑' if row[K_D] > 0 else '↓'}{row[K_D]}%"
    return rowStr


def __genIndustryRow(row) -> str:
    rowStr = ""
    rowStr += f"\n指數：{row[SYMBOL]}"
    rowStr += f"\n日期：{DateUtils.strformat(row[MARKET_DATE], constants.YYYYMMDD, constants.YYYYMMDD_SLASH)}"
    rowStr += f"\n收盤指數：{row[CLOSE]}"
    rowStr += f"\n漲跌點數：{__msgArrow(row[UPS_AND_DOWNS])}"
    rowStr += f"\n漲跌百分比(%)：{__msgArrow(row[UPS_AND_DOWNS_PCT])}%"
    return rowStr


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
        params = {
            "message": ("\n".join(msg))
        }

        response = requests.post(constants.NOTIFY_LINK, headers=headers, params=params, timeout=60)

        """
        200 => success
        414 => message too long
        """
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
        sendMsg(msg, token)
    except Exception as ex:
        CoreException.show_error(ex, traceback.format_exc())
        time.sleep(10)
    finally:
        time.sleep(2)


@interceptor
def sendImg(img: str, text: str, token=constants.TOKEN_SENSATIONAL):
    """ Sending picture through Line client """
    try:
        headers = {
            "Authorization": "Bearer " + token,
        }
        data = ({
            'message': [f"{DateUtils.default_msg(constants.YYYYMMDD_SLASH)} {text}! 👍"]
        })
        file = {
            'imageFile': open((constants.IMAGE_PATH % img), 'rb')
        }
        response = requests.post(constants.NOTIFY_LINK, headers=headers, files=file, data=data, timeout=60)

        """
        200 => success
        414 => message too long
        """
        log.debug(f"Response status: {response.status_code}")
        response.close()
    except requests.exceptions.ConnectionError as connError:
        CoreException.show_error(connError, traceback.format_exc())
        time.sleep(10)
        # Send notify again
        sendImg(img, token)
    except Exception as ex:
        CoreException.show_error(ex, traceback.format_exc())
        time.sleep(10)
    finally:
        time.sleep(2)


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
                msg.extend([__genStringRow(row)])

                # 1000 words limit with Line Notify
                if len(msg) % 9 == 0:
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
def sendIndustry(df: DataFrame):
    default = f"{DateUtils.default_msg(constants.YYYYMMDD_SLASH)}{NotifyGroup.INDEX.getValue()}"
    msg = [default]

    if not df.empty:
        for index, row in df.iterrows():
            # FIXME 暫定漲跌百分比 > 0的資料
            if row[UPS_AND_DOWNS_PCT] > 0:
                # extend => extract whatever types of element inside a list
                msg.extend([__genIndustryRow(row)])

                # 1000 words limit with Line Notify
                if len(msg) % 9 == 0:
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

    """ KD, BollingBand """
    FunctionBollingBand.GenBollingerBand(data)
    FunctionBollingBand.BuySellSignal(data)

    """ MA cross rate """
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
            """ https://www.maxlist.xyz/2020/03/20/multi-processing-pool/ """
            # Multiprocessing 設定處理程序數量 (pools = Pool(4))
            pools = Pool(multiprocessing.cpu_count() - 1)
            results = pools.map(func=genNotifyData, iterable=symbols)

            # results = processPools.starmap_async(genNotifyData,
            #                                      zip(symbols, repeat(pool)),
            #                                      callback=CoreException.show,
            #                                      error_callback=CoreException.show_error)

            # results = processPools.map_async(func=genNotifyData,
            #                                  iterable=symbols,
            #                                  callback=CoreException.show,
            #                                  error_callback=CoreException.error)
            # 關閉process的pool並等待所有process結束
            # processPools.close()
            # processPools.join()

            # 包含Key資料的dictionary
            if len(results) > 0:
                if not NotifyGroup.POTENTIAL in stockDict:
                    """ Riley's stocks (from line_notify.py) """
                    for row in results:
                        print(row)
                        if (row[RSI]) >= 70:
                            # 趕快賣的股票
                            stockDict[NotifyGroup.SELL].append(row)
                        elif row[RSI] <= 30:
                            # 好可憐的股票
                            stockDict[NotifyGroup.BAD].append(row)
                        else:
                            """ KD, BollingBand """
                            if row[SGNL_B]:
                                # 進場做多
                                stockDict[NotifyGroup.LONG].append(row)
                            elif row[SGNL_S]:
                                # 進場做空
                                stockDict[NotifyGroup.SHORT].append(row)

                            # """ MA cross rate """
                            # if row[RSI] >= 50 and row[POS] > 0:
                            #     # 進場做多
                            #     stockDict[NotifyGroup.LONG].append(row)
                            # elif row[RSI] < 50 and row[POS] < 0:
                            #     # 進場做空
                            #     stockDict[NotifyGroup.SHORT].append(row)

                            else:
                                # 徘徊不定的股票
                                stockDict[NotifyGroup.NORMAL].append(row)
                else:
                    """ Portential stocks (from potential_stock.py) """
                    for row in results:
                        stockDict[NotifyGroup.POTENTIAL].append(row)

                # 送出Line Notify
                sendNotify(stockDict)
    except Exception:
        raise


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)

    try:
        stocks = constants.RILEY_STOCKS
        log.debug(f"Symbols: {stocks}")
        arrangeNotify(stocks, NotifyGroup.getLineGroup())

        # sendImg('Complete3.png')
        sendMsg([ms, constants.SUCCESS % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        sendMsg([ms, constants.FAIL % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
