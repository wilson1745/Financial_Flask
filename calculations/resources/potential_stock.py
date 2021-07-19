# -*- coding: UTF-8 -*-
"""
https://www.finlab.tw/Python-%E6%99%82%E9%96%93%E5%BA%8F%E5%88%97%E5%AF%A6%E4%BD%9C%EF%BC%81/
https://www.finlab.tw/%E5%8A%A0%E9%80%9F%E5%BA%A6%E6%8C%87%E6%A8%99%E5%AF%A6%E5%81%9A/
"""
import collections
import datetime
import multiprocessing
import os
import sys
import time
import traceback
from multiprocessing.pool import ThreadPool as Pool

import pandas as pd
from pandas import DataFrame

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.constants import CLOSE, SYMBOL
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_line_notify import NotifyGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo
from calculations.resources import line_notify


@interceptor
def cal_dropdown_rate(df: DataFrame):
    """ 計算近n年最大下跌幅度 """
    dropdown = (df.cummax() - df).max() / df.max() * 100
    # print(dropdown)

    # 計算近n年報酬率
    profit = (df.iloc[-1] / df.iloc[0] - 1) * 100
    # log.debug(profit)

    # 計算近n年標準差(波動率)
    std = (df / df.shift()).std() * 200
    # log.debug(std)

    """
    波動率 < 2％：波動率越大代表股價變化幅度越大，我們只選波動率小的股票
    獲利 > 10%：近三年報酬率大於10的股票
    最大下跌幅度 < 50%：下跌幅度也不能太大
    """
    constraint = std[std < 0.02].index & profit[profit > 10].index & dropdown[dropdown < 50].index
    # constraint = profit[profit > 10].index & dropdown[dropdown < 50].index
    # log.debug(constraint)
    return constraint


@interceptor
def crawl_price(dateP: str):
    df = dailystock_repo.findLikeYear(dateP)
    if not df.empty:
        df.reset_index(drop=True, inplace=True)
        df = df.set_index(SYMBOL)
        data[dateP] = df


@interceptor
def rising_curve(n):
    return (close60.iloc[-n] + close60.iloc[-1]) / 2 > close60.iloc[-int((n + 1) / 2)]


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    data: dict = {}
    fileName = os.path.basename(__file__)

    try:
        dateList = []
        date = datetime.datetime.now()
        n_days = 200

        while len(dateList) < n_days:
            dateStr = datetime.datetime.strftime(date, constants.YYYYMMDD)
            dateList.append(dateStr)

            # 減一天
            date -= datetime.timedelta(days=1)

        dateList.reverse()
        log.debug(f"dateList: {dateList}")

        """ Do not use all my processing power """
        pools = Pool(multiprocessing.cpu_count() - 1)
        pools.map(func=crawl_price, iterable=dateList)

        # Sort order by market_date
        data = collections.OrderedDict(sorted(data.items()))
        # log.debug(f"data: {data}")

        # 扁平化資料面
        close = pd.DataFrame({k: d[CLOSE] for k, d in data.items()}).transpose()
        close.index = pd.to_datetime(close.index)
        # log.debug(f"close: {close}")

        # 60 days moving average
        close60 = close.rolling(60, min_periods=10).mean()

        rising = (
                rising_curve(5) &
                rising_curve(10) &
                rising_curve(20) &
                rising_curve(60) &
                rising_curve(30) &
                rising_curve(40) &
                rising_curve(50) &
                (close.iloc[-1] > close60.iloc[-1])
        )

        potentials: list = rising[rising].index
        log.debug(f"Rising stock: {potentials}")

        # Send Line Notify
        line_notify.arrangeNotify(potentials, NotifyGroup.getPotentialGroup())

        line_notify.sendMsg([ms, constants.SUCCESS % fileName], constants.TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        line_notify.sendMsg([ms, constants.FAIL % fileName], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")
