# -*- coding: UTF-8 -*-
"""
https://www.finlab.tw/Python-%E6%99%82%E9%96%93%E5%BA%8F%E5%88%97%E5%AF%A6%E4%BD%9C%EF%BC%81/
https://www.finlab.tw/%E5%8A%A0%E9%80%9F%E5%BA%A6%E6%8C%87%E6%A8%99%E5%AF%A6%E5%81%9A/
"""
import collections
import datetime
import os
import traceback

import pandas as pd
from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame, Series

from calculations.common.constants.constants import CLOSE, FAIL, SUCCESS, SYMBOL, THREAD, YYYYMMDD
from calculations.common.enums.enum_line_notify import NotifyGroup
from calculations.common.enums.enum_notifytok import NotifyTok
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.http_utils import HttpUtils
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily


class PotentialStock(IFinancialDaily):
    """ 台股加速度指標 """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @classmethod
    @interceptor
    def __rising_curve(cls, close60, n) -> Series:
        """ Rising curve
        return Series like:
        0050      False
        0051      False
        0052       True
        0053       True
        """
        # (n天前 + 當天)/2 > n/2天前 的k天均線
        return (close60.iloc[-n] + close60.iloc[-1]) / 2 > close60.iloc[-int((n + 1) / 2)]

    @classmethod
    @interceptor
    def __crawl_price(cls, data: dict, dateP: str):
        """ Crawl price """
        df = DailyStockRepo.find_like_year(dateP)
        if not df.empty:
            df.reset_index(drop=True, inplace=True)
            df = df.set_index(SYMBOL)
            data[dateP] = df

    # @classmethod
    # @interceptor
    # def __cal_dropdown_rate(cls, df: DataFrame):
    #     """ 計算近n年最大下跌幅度 """
    #     dropdown = (df.cummax() - df).max() / df.max() * 100
    #     # print(dropdown)
    #
    #     # 計算近n年報酬率
    #     profit = (df.iloc[-1] / df.iloc[0] - 1) * 100
    #     # log.debug(profit)
    #
    #     # 計算近n年標準差(波動率)
    #     std = (df / df.shift()).std() * 200
    #     # log.debug(std)
    #
    #     """
    #     波動率 < 2％：波動率越大代表股價變化幅度越大，我們只選波動率小的股票
    #     獲利 > 10%：近三年報酬率大於10的股票
    #     最大下跌幅度 < 50%：下跌幅度也不能太大
    #     """
    #     constraint = std[std < 0.02].index & profit[profit > 10].index & dropdown[dropdown < 50].index
    #     # constraint = profit[profit > 10].index & dropdown[dropdown < 50].index
    #     # log.debug(constraint)
    #     return constraint

    @classmethod
    @interceptor
    def get_potentials(cls) -> list:
        data_dict: dict = {}
        dateList = []
        date = datetime.datetime.now()
        n_days = 200

        while len(dateList) < n_days:
            dateStr = datetime.datetime.strftime(date, YYYYMMDD)
            dateList.append(dateStr)
            # 減一天
            date -= datetime.timedelta(days=1)

        dateList.reverse()
        LOG.debug(f"dateList: {dateList}")

        # Get stock price from DailyStockRepo
        with parallel_backend(THREAD, n_jobs=-1):
            Parallel()(delayed(cls.__crawl_price)(data_dict, date) for date in dateList)

        # Sort order by market_date
        data = collections.OrderedDict(sorted(data_dict.items()))
        # log.debug(f"data: {data}")

        # 扁平化資料面
        close = pd.DataFrame({k: d[CLOSE] for k, d in data.items()}).transpose()
        close.index = pd.to_datetime(close.index)
        # log.debug(f"close: {close}")

        # 60 days moving average
        close60 = close.rolling(60, min_periods=10).mean()
        # LOG.debug(f"close60: {close60}")

        # 所有的條件做交集(&)
        rising = (
                cls.__rising_curve(close60, 5) &
                cls.__rising_curve(close60, 10) &
                cls.__rising_curve(close60, 20) &
                cls.__rising_curve(close60, 60) &
                cls.__rising_curve(close60, 30) &
                cls.__rising_curve(close60, 40) &
                cls.__rising_curve(close60, 50) &
                (close.iloc[-1] > close60.iloc[-1])
        )
        # LOG.debug(f"rising: {rising}")

        # 從rising這條序列中，選取rising為 True的股票，忽略False的股票
        potentials: list = rising[rising].index
        LOG.debug(f"Rising symbols: {potentials}")
        return potentials

    @staticmethod
    @interceptor
    def query_data(symbol: str) -> DataFrame:
        """ DailyStockRepo """
        LOG.debug(f"Start genNotifyStr: {symbol} at {datetime.datetime.now()} ")
        data_df = DailyStockRepo.find_by_symbol(symbol)
        return data_df

    @classmethod
    @interceptor
    def main_daily(cls) -> dict:
        """ Potential DailyStock的主程式 """
        lineNotify = HttpUtils()
        try:
            potentials = cls.get_potentials()

            # 產生DailyFund的notify訊息
            with parallel_backend(THREAD, n_jobs=-1):
                df_list = Parallel()(delayed(cls.query_data)(symbol) for symbol in potentials)
            stocks_dict = NotifyUtils.arrange_notify(df_list, NotifyGroup.getPotentialGroup())

            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return stocks_dict
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            # Get data
            stock_dict = cls.main_daily()

            # Send notify
            NotifyUtils.send_notify(stock_dict, HttpUtils(NotifyTok.MINE))
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    PotentialStock.main()
