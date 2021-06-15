""" Reference: https://pyecontech.com/2019/05/20/python%e8%99%95%e7%90%86%e9%87%91%e8%9e%8d%e8%b3%87%e6%96%99-p-1-%e7
%94%a8pandas%e8%88%87matplotlib%e4%be%86%e7%95%ab%e8%82%a1%e5%83%b9%e5%9c%96/ """
import traceback

import pandas
from pandas import DataFrame

from calculations import log
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor


# 計算KD線
from calculations.repository import dailystock_repo


@interceptor
def GetDataKD(data) -> DataFrame:
    """
    Step1:計算RSV:(今日收盤價-最近9天的最低價)/(最近9天的最高價-最近9天的最低價)
    Step2:計算K: K = 2/3 X (昨日K值) + 1/3 X (今日RSV)
    Step3:計算D: D = 2/3 X (昨日D值) + 1/3 X (今日K值)
    """
    data_df = data.copy()
    data_df["min"] = data_df["lowest_price"].rolling(9).min()
    data_df["max"] = data_df["highest_price"].rolling(9).max()
    data_df["RSV"] = (data_df["close_price"] - data_df["min"]) / (data_df["max"] - data_df["min"])
    data_df = data_df.dropna()

    # 計算K
    # K的初始值定為50
    K_list = [50]
    for num, rsv in enumerate(list(data_df["RSV"])):
        K_yestarday = K_list[num]
        K_today = 2 / 3 * K_yestarday + 1 / 3 * rsv
        K_list.append(K_today)
    data_df["K"] = K_list[1:]

    # 計算D
    # D的初始值定為50
    D_list = [50]
    for num, K in enumerate(list(data_df["K"])):
        D_yestarday = D_list[num]
        D_today = 2 / 3 * D_yestarday + 1 / 3 * K
        D_list.append(D_today)
    data_df["D"] = D_list[1:]

    # 調整百分比和小數點
    data_df[["K", "D"]] = data_df[["K", "D"]].apply(lambda rs: round(rs * 100, 2))
    # log.debug(data_df)

    use_df = pandas.merge(data, data_df[["K", "D"]], left_index=True, right_index=True, how="left")
    # use_df = use_df.dropna()
    # log.debug(f"KD data: {use_df}")

    return use_df


# ------------------- App Start -------------------
if __name__ == "__main__":
    try:
        stock = dailystock_repo.findBySymbol("3231")
        result = GetDataKD(stock)

        log.debug(result)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
