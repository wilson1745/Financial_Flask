"""
Reference:
https://pyecontech.com/2019/06/26/%e5%88%9d%e5%ad%b8%e8%80%85%e7%9a%84python%e9%87%91%e8%9e%8d%e5%88%86%e6%9e%90%e6%97%a5%e8%a8%98-ep6-rsi/
"""
import time
import traceback

import matplotlib.pyplot as plt
from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import CLOSE_PRICE, RSI
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo


# @interceptor
def cal_U(num):
    if num >= 0:
        return num
    else:
        return 0


# @interceptor
def cal_D(num):
    num = -num
    return cal_U(num)


@interceptor
def plot(data):
    """ Render plot """
    plt.figure(figsize=(10, 10))
    data[RSI].plot()
    plt.plot(stock.index, [70] * len(stock.index))
    plt.plot(stock.index, [30] * len(stock.index))
    plt.legend()
    plt.show()


@interceptor
def GetDataRSI(data: DataFrame):
    """ 清理資料 成交股數、開盤價、最高價、最低價、收盤價的資料，並使用Date當作索引值 """

    # stock.index = pd.to_datetime(stock["market_date"])
    # stock.set_index(pd.todatetime(stock["market_date"], format="%Y/%m/%d"), inplace=True)

    """ No need to choose column (maybe???) """
    # data = data[["market_date", "stock_name", "symbol", "deal_stock", "opening_price", "highest_price", "lowest_price", "close_price"]]

    # stock["close_price"] = pd.to_numeric(stock["close_price"])
    # stock = stock["2021-01-20":]

    """ Get the Diff price. Important!!!!! """
    data["Dif"] = data[CLOSE_PRICE].diff()
    # print(stock)

    data["cal_U"] = data["Dif"].apply(cal_U)
    data["cal_D"] = data["Dif"].apply(cal_D)
    data["ema_U"] = data["cal_U"].ewm(span=14).mean()
    data["ema_D"] = data["cal_D"].ewm(span=14).mean()
    data["RS"] = data["ema_U"].div(data["ema_D"])
    data[RSI] = data["RS"].apply(lambda rs: round(rs / (1 + rs) * 100, 2))
    # log.debug(f"RSI data: {data}")


# ------------------- App Start -------------------
if __name__ == "__main__":
    now = time.time()
    try:
        # Get history data
        stock = dailystock_repo.findBySymbol("3231")

        # Generate RSI
        GetDataRSI(stock)
        # log.debug(stock)

        # Making picture
        plot(stock)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
