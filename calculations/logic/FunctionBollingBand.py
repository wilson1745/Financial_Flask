import traceback

import talib
from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import CLOSE, D, K, LOWER, MIDDLE, SGNL_B, SGNL_S, UPPER
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.logic import FunctionKD
from calculations.repository.dailystock_repo import DailyStockRepo


@interceptor
def GenBollingerBand(df: DataFrame):
    """ 計算布林通道 """
    # 創建布林通道： 週期 20日（＝日K月均線）、1個標準差
    # BBAND20 = abstract.BBANDS(df, timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
    df[UPPER], df[MIDDLE], df[LOWER] = talib.BBANDS(df[CLOSE], timeperiod=20, nbdevup=1, nbdevdn=1, matype=2)
    data = df.dropna()


@interceptor
def BuySellSignal(df: DataFrame):
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


# ------------------- App Start -------------------
if __name__ == "__main__":
    try:
        stock_df = DailyStockRepo.find_by_symbol("2324")
        # result = GetDataKD(stock)
        # log.debug(result.tail())

        FunctionKD.GenKD(stock_df)
        GenBollingerBand(stock_df)
        BuySellSignal(stock_df)

        # log.debug(stock.tail())
        log.debug(stock_df)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
