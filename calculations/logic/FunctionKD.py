# -*- coding: UTF-8 -*-
"""
https://pyecontech.com/2019/05/20/python%e8%99%95%e7%90%86%e9%87%91%e8%9e%8d%e8%b3%87%e6%96%99-p-1-%e7%94%a8pandas%e8%88%87matplotlib%e4%be%86%e7%95%ab%e8%82%a1%e5%83%b9%e5%9c%96/
"""
import traceback

from pandas import DataFrame

from calculations.common.constants.constants import CLOSE, D, HIGH, K, LOW
from calculations.common.exceptions.core_exception import CoreException
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.dailyfund_repo import DailyFundRepo


@interceptor
def GenKD(df: DataFrame):
    """
    計算KD線
    Step1:計算RSV:(今日收盤價-最近9天的最低價)/(最近9天的最高價-最近9天的最低價)
    Step2:計算K: K = 2/3 X (昨日K值) + 1/3 X (今日RSV)
    Step3:計算D: D = 2/3 X (昨日D值) + 1/3 X (今日K值)
    """
    data_df = df.copy()
    data_df['min'] = data_df[LOW].rolling(9).min()
    data_df['max'] = data_df[HIGH].rolling(9).max()
    data_df['RSV'] = (data_df[CLOSE] - data_df['min']) / (data_df['max'] - data_df['min'])
    data_df.dropna(inplace=True)

    # today_multi = lambda x, y: 2 / 3 * x + 1 / 3 * y

    # 計算K (K的初始值定為50)
    K_list = [50]
    for num, rsv in enumerate(list(data_df['RSV'])):
        K_yestarday = K_list[num]
        K_today = 2 / 3 * K_yestarday + 1 / 3 * rsv
        K_list.append(K_today)
    data_df[K] = K_list[1:]

    # 計算D (D的初始值定為50)
    D_list = [50]
    for num, k_value in enumerate(list(data_df[K])):
        D_yestarday = D_list[num]
        D_today = 2 / 3 * D_yestarday + 1 / 3 * k_value
        D_list.append(D_today)
    data_df[D] = D_list[1:]

    # 調整成百分比和小數點
    data_df[[K, D]] = data_df[[K, D]].apply(lambda rs: round(rs * 100, 2))

    # merge pandas的一種方式
    # data = pandas.merge(data, data_df[[K, D]], left_index=True, right_index=True, how='left')
    # 直接指定column給原索引
    df[[K, D]] = data_df[[K, D]]
    df.dropna(inplace=True)
    # log.debug(f"KD data: {data}")


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    try:
        # stock = DailyStockRepo.find_by_symbol('2330')
        stock = DailyFundRepo.find_by_symbol('B09%2C012')

        GenKD(stock)
        # log.debug(stock.tail())
        LOG.debug(stock)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
