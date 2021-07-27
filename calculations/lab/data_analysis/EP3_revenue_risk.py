# -*- coding: UTF-8 -*-
"""
Reference:
https://pyecontech.com/2019/06/18/%e5%88%9d%e5%ad%b8%e8%80%85%e7%9a%84python%e9%87%91%e8%9e%8d%e5%88%86%e6%9e%90%e6%97%a5%e8%a8%98-ep3-%e8%82%a1%e7%a5%a8%e6%94%b6%e7%9b%8a%e7%8e%87%e8%88%87%e9%a2%a8%e9%9a%aa%e8%a9%95%e4%bc%b0/
"""
import matplotlib.pyplot as plt

from calculations.common.utils.constants import CLOSE, MARKET_DATE, SYMBOL
from calculations.core.Interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo


@interceptor
def main_start():
    symbols = ["2330", "0056", "00881", "2324", "2441", "2401"]

    # Get data with all symbols
    stocks_dict = {}
    for symbol in symbols:
        stocks_dict.update({symbol: DailyStockRepo.find_by_symbol(symbol)})

    # Generate key
    for key in stocks_dict.keys():
        df = stocks_dict[key]
        df.index = df[MARKET_DATE]
        df = df[[SYMBOL, CLOSE]]
        df.columns = [SYMBOL, CLOSE]
        stocks_dict[key] = df

    fig, ax = plt.subplots(len(symbols), 1, figsize=(10, 10))
    plt.subplots_adjust(hspace=0.8)
    for i in range(len(symbols)):
        if i % 2 == 0:
            print("Double")
        else:
            print("Odd")
        stocks_dict[symbols[i]]['2020-01-01':].plot(ax=ax[i])
        ax[i].set_title(symbols[i])

    fig.suptitle('Stock Price via time')
    plt.show()

    # fig, ax = plt.subplots(3, 2, figsize=(10, 10))
    # plt.subplots_adjust(hspace=0.8)
    #
    # df = data.copy()
    # df_p = df['2020-01-01':].iloc[:-1, :]
    # df_a = df['2020-01-01':].iloc[1:, :]
    # plt.scatter(np.array(df_p['close_price']), np.array(df_a['close_price']))
    # plt.show()
    #
    # plt.hist([np.array(df['2020-01-01':'2020-09-01']['close_price']),
    #           np.array(df['2020-09-01':]['close_price'])])

    # df_lrp = df.iloc[:-1, :]
    # df_lra = df.iloc[1:, :]
    # plt.scatter(np.array(df_lrp['linear return rate']),
    #             np.array(df_lra['linear return rate']))
    # plt.show()

    # fig, axes = plt.subplots(2, 1)
    #
    # data = pd.Series(np.random.rand(16), index=list('abcdefghijklmnop'))
    #
    # data.plot.bar(ax=axes[0], color='b', alpha=0.5)
    # data.plot.barh(ax=axes[1], color='k', alpha=0.5)
    # plt.show()


# ------------------- App Start -------------------
if __name__ == '__main__':
    main_start()
