# -*- coding: UTF-8 -*-
import pandas as pd
import talib
from pandas import DataFrame

from calculations.common.utils.constants import CLOSE, RSI
from calculations.logic import FunctionKD
from calculations.repository.dailystock_repo import DailyStockRepo

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)

symbol = "2330"
df: DataFrame = DailyStockRepo.find_by_symbol(symbol)
# df = DataFrameUtils.dfForTalib(df)
# df = df.astype('float')

smoothK = 3
smoothD = 3
lengthRSI = 14
# fastk_period
lengthStoch = 14

# print(df[CLOSE].to_numpy())

df[RSI] = talib.RSI(df[CLOSE], timeperiod=12)
df.dropna(inplace=True)
# rsi  = tulipy.rsi(df[CLOSE].to_numpy(), 12)


# df[K], df[D] = talib.STOCH(df[HIGH], df[LOW], df[CLOSE],
#                            fastk_period=9,
#                            slowk_period=3,
#                            slowk_matype=MA_Type.SMA,
#                            slowd_period=3,
#                            slowd_matype=MA_Type.SMA)

df = FunctionKD.GetDataKD(df)

# df['fastK'], df['fastD'] = talib.STOCHF(df[HIGH], df[LOW], df[CLOSE],
#                                         fastk_period=9,
#                                         fastd_period=3,
#                                         fastd_matype=MA_Type.SMA)

df = df.round(2)
print(df.tail())

# print(df.tail())
# rsinp = df[RSI].values
# rsinp = rsinp[np.logical_not(np.isnan(rsinp))]
# fastk, fastd = tulipy.stoch(
#     df[HIGH].to_numpy(),
#     df[LOW].to_numpy(),
#     df[CLOSE].to_numpy(), 9, 3, 9)
# fastk = [round(i, 2) for i in fastk]
# fastd = [round(i, 2) for i in fastd]
# print(fastk)
# print(fastd)

# k = tulipy.sma(tulipy.stoch(
#     high=df[HIGH].to_numpy(),
#     low=df[LOW].to_numpy(),
#     close=df[CLOSE].to_numpy(),
#     pct_k_period=9,
#     pct_k_slowing_period=3,
#     pct_d_period=9), 3)
# d = tulipy.sma(k, 3)
# print(k)
# print(d)

# stochInd = talib.STOCHRSI(df[CLOSE], Closetimeperiod=12, fastk_period=9, fastd_period=9, fastd_matype=0)
# sRSI_d = stochInd.stochrsi_d() * 100
# sRSI_k = stochInd.stochrsi_k() * 100
# print(sRSI_k)
# print(sRSI_d)

# k = tulipy.sma(tulipy.stoch(high=rsi1, low=rsi1, close=rsi1, pct_k_period=lengthStoch, pct_k_slowing_period=smoothK, pct_d_period=smoothD), smoothK)
# d = tulipy.sma(k, smoothD)

# rsinp = df[RSI].values
# rsinp = [round(i, 2) for i in rsinp]
# rsinp = rsinp[np.logical_not(np.isnan(rsinp))]
#
# # print(rsinp)
# fastk, fastd = tulipy.stoch(
#     high=rsinp,
#     low=rsinp,
#     close=rsinp,
#     pct_k_period=lengthStoch,
#     pct_k_slowing_period=smoothK,
#     pct_d_period=smoothD)
#
# fastk = [round(i, 2) for i in fastk]
# fastd = [round(i, 2) for i in fastk]
#
# print(fastk)
# print(fastd)

# k = tulipy.sma(tulipy.stoch(high=rsi1, low=rsi1, close=rsi1, pct_k_period=lengthStoch, pct_k_slowing_period=smoothK, pct_d_period=smoothD), smoothK)
# d = tulipy.sma(k, smoothD)
#
# print(df.tail())

# df[RSI] = talib.RSI(df[CLOSE], timeperiod=12)
# # print(df[RSI])
#
# # df[K], df[D] = talib.STOCHF(df[RSI], df[RSI], df[RSI], fastk_period=20, fastd_period=20, fastd_matype=MA_Type.SMA)
#
# df['slowk'], df['slowd'] = talib.STOCH(df[HIGH], df[LOW], df[CLOSE],
#                                        fastk_period=9,
#                                        slowk_period=3,
#                                        slowk_matype=0,
#                                        slowd_period=3,
#                                        slowd_matype=0)
#
# df['fastk'], df['fastd'] = talib.STOCHF(df[HIGH], df[LOW], df[CLOSE],
#                                         fastk_period=9,
#                                         fastd_period=9,
#                                         fastd_matype=0)
#
# df['STOCHRSIk'], df['STOCHRSId'] = talib.STOCHRSI(df[CLOSE],
#                                                   timeperiod=12,
#                                                   fastk_period=9,
#                                                   fastd_period=9,
#                                                   fastd_matype=0)
#
# # df[K], df[D] = talib.STOCH(df[HIGH], df[LOW], df[CLOSE])
#
# # stochf = [round(i, 2) for i in stochf]
#
# df = df.round(2)
# print(df.tail())
