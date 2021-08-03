"""
https://hahow.in/creations/5b175848567cc1001e401c0c
"""
import os
import time
import traceback

import pandas as pd
import talib
from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.constants import CLOSE, D, K
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.logic import FunctionKD, FunctionRSI
from calculations.repository.dailystock_repo import DailyStockRepo

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


@interceptor
def GenBollingerBand(data: DataFrame):
    """ 計算布林通道 """

    # 創建布林通道： 週期 20日（＝日K月均線）、1個標準差
    # BBAND20 = abstract.BBANDS(df, timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
    data['upper'], data['middle'], data['lower'] = talib.BBANDS(data[CLOSE], timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
    data = data.dropna()
    print(data)


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    try:
        RILEY_STOCKS = ["0050", "0056", "00881", "1802", "2303", "2330", "2324", "2375", "2401", "2441", "2617", "3231", "6116"]

        symbol = '2497'
        df: DataFrame = DailyStockRepo.find_by_symbol(symbol)

        # 計算KD, RSI
        FunctionRSI.GenRSI(df)
        FunctionKD.GenKD(df)

        # Talib KD (not accurate)
        # df[K], df[D] = talib.STOCH(df[HIGH],
        #                            df[LOW],
        #                            df[CLOSE],
        #                            fastk_period=9,
        #                            slowk_period=3,
        #                            slowk_matype=1,
        #                            slowd_period=3,
        #                            slowd_matype=1)

        # 創建布林通道： 週期 20日（＝日K月均線）、1個標準差
        # BBAND20 = abstract.BBANDS(df, timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
        df['upper'], df['middle'], df['lower'] = talib.BBANDS(df[CLOSE], timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
        df = df.dropna()

        # data = dict(upper=upper, middle=middle, lower=lower)
        # df = pd.DataFrame(data, index=df.index, columns=['upper', 'middle', 'lower']).dropna()
        # print(df.tail(20))
        # print(df)

        # # 創建 KD 指標：（預設參數）
        # # STOCH = abstract.STOCH(df)
        # STOCH = talib.STOCH(df['close'])
        # print(STOCH)
        # STOCH = FunctionKD.GenKD(df)

        # 建立買進信號：KD在低檔（小於25）金叉，且收盤價仍在布林通道中線以下時。
        # df['sgnl_b'] = (df[K] < 25) & \
        #                (df[K] > df[D]) & \
        #                (df[K].shift() < df[D].shift()) & \
        #                (df[CLOSE] <= df['middle'])
        df['sgnl_b'] = (df[K] > df[D]) & \
                       (df[K].shift() < df[D].shift()) & \
                       (df[CLOSE] <= df['middle'])

        # print(sgnl_b)

        # 建立賣出信號：昨日收盤價仍在布林通道上緣，今日收盤價卻跌落布林通道上緣時。
        df['sgnl_s'] = (df[CLOSE] < df['upper']) & \
                       (df[CLOSE].shift() > df['upper'].shift())

        print(df)
        # print(df[K])
        # print(df.tail(150))
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        LOG.debug(f"Async time consuming: {time.time() - now}")
        LOG.debug(f"End of {os.path.basename(__file__)}")
