""" Reference: https://pyecontech.com/2019/06/22/%E5%88%9D%E5%AD%B8%E8%80%85%E7%9A%84python%E9%87%91%E8%9E%8D%E5%88
%86%E6%9E%90%E6%97%A5%E8%A8%98-ep5-%E7%A7%BB%E5%8B%95%E5%B9%B3%E5%9D%87%E3%80%81%E6%8C%87%E6%95%B8%E7%A7%BB%E5%8B%95
%E5%B9%B3// """
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import CLOSE_PRICE, HIGHEST_PRICE, LOWEST_PRICE, OPENING_PRICE, POS, VOLUME, MARKET_DATE
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo


@interceptor
def MA(price, days):
    ma = price.rolling(days).mean()
    ma.dropna(inplace=True)
    return ma


@interceptor
def GetCross(df: DataFrame, fastPeriod: int, slowPeriod: int) -> DataFrame:
    """ Calculate MA cross rate (https://zhuanlan.zhihu.com/p/38448602)"""
    fastMA = f'MA{fastPeriod}'
    slowMA = f'MA{slowPeriod}'

    df[fastMA] = df[CLOSE_PRICE].rolling(window=fastPeriod, center=False).mean().round(decimals=1)
    df[slowMA] = df[CLOSE_PRICE].rolling(window=slowPeriod, center=False).mean().round(decimals=1)

    # 删除空值
    # df[f'ma{period}'].dropna(inplace=True)
    df.dropna()

    # 持倉情況和交易信號判斷
    df[POS] = 0  # 初始化
    df.loc[df[fastMA] >= df[slowMA], POS] = 1
    df.loc[df[fastMA] < df[slowMA], POS] = -1
    df[POS] = df[POS].shift(1).fillna(0)

    return df


# 計算MA線
@interceptor
def GetMaData(sid):
    stock = dailystock_repo.findBySymbol(sid)

    # 清理資料並使用Date當作我們的索引值
    stock.index = pd.to_datetime(stock[MARKET_DATE])
    # print(stock.index)

    # 需要成交股數、開盤價、最高價、最低價、收盤價的資料
    stock = stock[[OPENING_PRICE, HIGHEST_PRICE, LOWEST_PRICE, CLOSE_PRICE, VOLUME]]

    # 分別計算7天,15天與30天的移動平均線
    stock["MA_7"] = MA(stock[CLOSE_PRICE], 7)
    log.debug(stock["MA_7"])

    stock["MA_15"] = MA(stock[CLOSE_PRICE], 15)
    log.debug(stock["MA_15"])

    stock["MA_30"] = MA(stock[CLOSE_PRICE], 30)
    log.debug(stock["MA_30"])

    # 指數移動平均線
    stock["EMA_12"] = stock[CLOSE_PRICE].ewm(span=12).mean()
    stock["EMA_26"] = stock[CLOSE_PRICE].ewm(span=26).mean()

    stock["DIF"] = stock["EMA_12"] - stock["EMA_26"]
    stock["DEM"] = stock["DIF"].ewm(span=9).mean()
    stock["OSC"] = stock["DIF"] - stock["DEM"]

    stock = stock["2021-01-01":]
    fig, ax = plt.subplots(3, 1, figsize=(10, 10))
    plt.subplots_adjust(hspace=0.8)
    stock["MA_7"].plot(ax=ax[0])
    stock["MA_15"].plot(ax=ax[0])
    stock["MA_30"].plot(ax=ax[0])
    stock["EMA_12"].plot(ax=ax[1])
    stock["EMA_26"].plot(ax=ax[1])
    stock[CLOSE_PRICE].plot(ax=ax[0])
    stock[CLOSE_PRICE].plot(ax=ax[1])
    ax[0].legend()
    ax[1].legend()
    stock["DIF"].plot(ax=ax[2])
    stock["DEM"].plot(ax=ax[2])
    ax[2].fill_between(stock.index, 0, stock["OSC"])
    ax[2].legend()
    plt.show()


# ------------------- App Test -------------------
if __name__ == "__main__":
    GetMaData("2330")
