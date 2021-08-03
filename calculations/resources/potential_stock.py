# -*- coding: UTF-8 -*-
"""
https://www.finlab.tw/Python-%E6%99%82%E9%96%93%E5%BA%8F%E5%88%97%E5%AF%A6%E4%BD%9C%EF%BC%81/
https://www.finlab.tw/%E5%8A%A0%E9%80%9F%E5%BA%A6%E6%8C%87%E6%A8%99%E5%AF%A6%E5%81%9A/
"""
import collections
import datetime
import multiprocessing
import os
import time
import traceback
from functools import partial
from multiprocessing.pool import ThreadPool

import pandas as pd
from joblib import parallel_backend, Parallel, delayed
from pandas import DataFrame

from calculations import LOG, CPU_THREAD
from calculations.common.utils.constants import CLOSE, FAIL, SUCCESS, SYMBOL, YYYYMMDD
from calculations.common.utils.enums.enum_line_notify import NotifyGroup
from calculations.common.utils.enums.enum_notifytok import NotifyTok
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily
from calculations.common.utils.line_utils import LineUtils
from projects.common.constants import THREAD


class PotentialStock(IFinancialDaily):
    """ 台股加速度指標 """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @classmethod
    @interceptor
    def __rising_curve(cls, close60, n):
        """ Rising curve """
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
        now = time.time()
        data_dict: dict = {}

        pools = ThreadPool(multiprocessing.cpu_count() - 1)
        lineNotify = LineUtils()
        try:
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

            # FIXME Do not use all my processing power
            with parallel_backend(THREAD, n_jobs=CPU_THREAD):
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

            potentials: list = rising[rising].index
            LOG.debug(f"Rising symbols: {potentials}")

            # 產生DailyFund的notify訊息
            with parallel_backend(THREAD, n_jobs=CPU_THREAD):
                df_list = Parallel()(delayed(cls.query_data)(symbol) for symbol in potentials)
            stocks_dict = NotifyUtils.arrange_notify(df_list, NotifyGroup.getPotentialGroup())

            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return stocks_dict
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise
        finally:
            LOG.debug(f"Time consuming: {time.time() - now}")
            pools.close()
            # pools.join()

    @classmethod
    @interceptor
    def main_daily_2(cls):
        """ Potential DailyStock的主程式 """
        now = time.time()
        data_dict: dict = {}

        pools = ThreadPool(multiprocessing.cpu_count())
        lineNotify = LineUtils()
        try:
            potentials = ['00625K', '00682U', '00683L', '00685L', '00711B', '00775B', '1533',
                          '1536', '1795', '2241', '2393', '2406', '2476', '2486', '3016', '3036A',
                          '3138', '3257', '3543', '3661', '3686', '4119', '4739', '4919', '4952',
                          '6128', '6552', '6715', '8996']

            # 產生DailyFund的notify訊息
            with parallel_backend('threading', n_jobs=CPU_THREAD):
                df_list = Parallel()(delayed(cls.query_data)(symbol) for symbol in potentials)

            # df_list = pools.map(func=cls.query_data, iterable=potentials)
            # with parallel_backend("multiprocessing", n_jobs=multiprocessing.cpu_count()):
            #     df_list = Parallel()(delayed(cls.query_data)(symbol) for symbol in potentials)

            # print(df_list)

            stocks_dict = NotifyUtils.arrange_notify(df_list, NotifyGroup.getPotentialGroup())

            # lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return stocks_dict
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise
        finally:
            LOG.debug(f"Time consuming: {time.time() - now}")
            pools.close()
            # pools.join()

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            # Get data
            stock_dict = cls.main_daily()
            # stock_dict = cls.main_daily_2()

            # Send notify
            NotifyUtils.send_notify(stock_dict, LineUtils(NotifyTok.RILEY))
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())


# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     PotentialStock.main()
