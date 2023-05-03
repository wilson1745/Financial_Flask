# -*- coding: UTF-8 -*-
"""
https://hahow.in/creations/5b175848567cc1001e401c0c
"""
import os
import sys
import traceback
import matplotlib.pyplot as plt

import talib
from pandas import DataFrame

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations.common.constants.constants import CLOSE, D, K, LOWER, MIDDLE, SGNL_B, SGNL_S, UPPER
from calculations.common.exceptions.core_exception import CoreException
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.logic import FunctionKD
from calculations.repository.dailyfund_repo import DailyFundRepo


@interceptor
def GenBollingerBand(df: DataFrame):
    """ 計算布林通道 """
    # 創建布林通道： 週期 20日（＝日K月均線）、1個標準差
    # BBAND20 = abstract.BBANDS(df, timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
    df[UPPER], df[MIDDLE], df[LOWER] = talib.BBANDS(df[CLOSE], timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
    df.dropna(inplace=True)


@interceptor
def BuySellSignal(df: DataFrame):
    """ 建立買進或賣出信號  """
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


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    try:
        # stock_df = DailyStockRepo.find_by_symbol("2330")
        stock_df = DailyFundRepo.find_by_symbol('B1qJzxf')

        FunctionKD.GenKD(stock_df)
        GenBollingerBand(stock_df)
        BuySellSignal(stock_df)

        LOG.debug(stock_df)

        ax = plt.gca()
        stock_df.plot(kind='line', x='market_date', y='close', ax=ax)
        stock_df.plot(kind='line', x='market_date', y='upper', color='red', ax=ax)
        stock_df.plot(kind='line', x='market_date', y='middle', color='green', ax=ax)
        stock_df.plot(kind='line', x='market_date', y='lower', color='red', ax=ax)
        plt.show()
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    # finally:
    #     os.system("pause")
