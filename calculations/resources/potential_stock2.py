# -*- coding: UTF-8 -*-
"""
https://hahow.in/creations/5b175848567cc1001e401c0c
"""
import multiprocessing
import os
import sys
import time
import traceback
from multiprocessing.pool import ThreadPool as Pool

from pandas import DataFrame

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.constants import CLOSE, D, K, MIDDLE, SGNL_B, SGNL_S, UPPER
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo
from calculations.resources import line_notify


@interceptor
def buy_sell_signal(df: DataFrame):
    """ TODO """
    # 建立買進信號：KD在低檔（小於25）金叉，且收盤價仍在布林通道中線以下時。
    # df[SGNL_B] = (df[K] < 25) & \
    #                (df[K] > df[D]) & \
    #                (df[K].shift() < df[D].shift()) & \
    #                (df[CLOSE] <= df[MIDDLE])
    df[SGNL_B] = (df[K] > df[D]) & \
                 (df[K].shift() < df[D].shift()) & \
                 (df[CLOSE] <= df[MIDDLE])

    # 建立賣出信號：昨日收盤價仍在布林通道上緣，今日收盤價卻跌落布林通道上緣時。
    df[SGNL_S] = (df[CLOSE] < df[UPPER]) & \
                 (df[CLOSE].shift() > df[UPPER].shift())


@interceptor
def main():
    """ Main program """
    # symbols = dailystock_repo.findAllSymbolGroup().index.tolist()
    # print(symbols)
    symbols = ["0050", "0056", "00881", "1802", "2303"]

    pools = Pool(multiprocessing.cpu_count() - 1)
    results = pools.map(func=dailystock_repo.findBySymbol, iterable=symbols)
    print(results)


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    data: dict = {}
    fileName = os.path.basename(__file__)

    try:
        main()

        # line_notify.sendMsg([ms, constants.SUCCESS % fileName], constants.TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        line_notify.sendMsg([ms, constants.FAIL % fileName], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")
