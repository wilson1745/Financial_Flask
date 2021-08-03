# -*- coding: UTF-8 -*-
"""
Reference:
https://pyecontech.com/2019/06/22/%E5%88%9D%E5%AD%B8%E8%80%85%E7%9A%84python%E9%87%91%E8%9E%8D%E5%88%86%E6%9E%90%E6%97%A5%E8%A8%98-ep5-%E7%A7%BB%E5%8B%95%E5%B9%B3%E5%9D%87%E3%80%81%E6%8C%87%E6%95%B8%E7%A7%BB%E5%8B%95%E5%B9%B3//
"""
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.constants import CLOSE, HIGH, LOW, MARKET_DATE, OPEN, POS, VOLUME
from calculations.core.Interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo


@interceptor
def MA(price, days):
    ma = price.rolling(days).mean()
    ma.dropna(inplace=True)
    return ma


@interceptor
def GetCross(df: DataFrame, fastPeriod: int = 5, slowPeriod: int = 15) -> DataFrame:
    """ Calculate MA cross rate (https://zhuanlan.zhihu.com/p/38448602)
    :param df 資料
    :param fastPeriod 預設快線
    :param slowPeriod 預設慢線
    """
    FAST_MA = f'MA{fastPeriod}'
    SLOW_MA = f'MA{slowPeriod}'

    df[FAST_MA] = df[CLOSE].rolling(window=fastPeriod, center=False).mean().round(decimals=1)
    df[SLOW_MA] = df[CLOSE].rolling(window=slowPeriod, center=False).mean().round(decimals=1)

    # 處理(删除)空值
    # df.dropna()
    df.fillna(0, inplace=True)

    # 持倉情況和交易信號判斷
    df[POS] = 0  # 初始化
    df.loc[df[FAST_MA] >= df[SLOW_MA], POS] = 1
    df.loc[df[FAST_MA] < df[SLOW_MA], POS] = -1
    df[POS] = df[POS].shift(1).fillna(0)
    # log.debug(df)

    return df


@interceptor
def GetMaData(sid):
    """ 計算MA線 """
    df = DailyStockRepo.find_by_symbol(sid)

    # 清理資料並使用Date當作我們的索引值
    df.index = pd.to_datetime(df[MARKET_DATE])
    # log.debug(stock.index)

    # 需要成交股數、開盤價、最高價、最低價、收盤價的資料
    df = df[[OPEN, HIGH, LOW, CLOSE, VOLUME]]

    # 分別計算7天,15天與30天的移動平均線
    df["MA_7"] = MA(df[CLOSE], 7)
    LOG.debug(df["MA_7"])

    df["MA_15"] = MA(df[CLOSE], 15)
    LOG.debug(df["MA_15"])

    df["MA_30"] = MA(df[CLOSE], 30)
    LOG.debug(df["MA_30"])

    # 指數移動平均線
    df["EMA_12"] = df[CLOSE].ewm(span=12).mean()
    df["EMA_26"] = df[CLOSE].ewm(span=26).mean()

    df["DIF"] = df["EMA_12"] - df["EMA_26"]
    df["DEM"] = df["DIF"].ewm(span=9).mean()
    df["OSC"] = df["DIF"] - df["DEM"]

    df = df["2021-01-01":]
    fig, ax = plt.subplots(3, 1, figsize=(10, 10))
    plt.subplots_adjust(hspace=0.8)
    df["MA_7"].plot(ax=ax[0])
    df["MA_15"].plot(ax=ax[0])
    df["MA_30"].plot(ax=ax[0])
    df["EMA_12"].plot(ax=ax[1])
    df["EMA_26"].plot(ax=ax[1])
    df[CLOSE].plot(ax=ax[0])
    df[CLOSE].plot(ax=ax[1])
    ax[0].legend()
    ax[1].legend()
    df["DIF"].plot(ax=ax[2])
    df["DEM"].plot(ax=ax[2])
    ax[2].fill_between(df.index, 0, df["OSC"])
    ax[2].legend()
    plt.show()


# ------------------- App Test -------------------
if __name__ == "__main__":
    symbol = "2330"

    GetMaData("2330")

    # data = dailystock_repo.findBySymbol(symbol)
    # data = GetCross(data)
