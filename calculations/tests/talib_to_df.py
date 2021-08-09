# -*- coding: UTF-8 -*-
import pandas as pd
import talib
from pandas import DataFrame
from talib._ta_lib import MA_Type

from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.repository.dailystock_repo import DailyStockRepo

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)

symbol = "2330"

df: DataFrame = DailyStockRepo.find_by_symbol(symbol)
df = DataFrameUtils.df_for_talib(df)

# 確認價量資料表 df 的值都是 float 格式
df = df.astype('float')

# 準備一份你想要計算並且併入 df 的技術指標清單
ta_list = ['MACD', 'STOCH', 'RSI']
# 這裡示範全部 158 種技術指標
# ta_list = talib.get_functions()
"""
['HT_DCPERIOD', 'HT_DCPHASE', 'HT_PHASOR', 'HT_SINE', 'HT_TRENDMODE', 'ADD', 'DIV', 'MAX', 'MAXINDEX', 'MIN', 'MININDEX', 'MINMAX',
'MINMAXINDEX', 'MULT', 'SUB', 'SUM', 'ACOS', 'ASIN', 'ATAN', 'CEIL', 'COS', 'COSH', 'EXP', 'FLOOR', 'LN', 'LOG10', 'SIN', 'SINH', 'SQRT', 'TAN',
'TANH', 'ADX', 'ADXR', 'APO', 'AROON', 'AROONOSC', 'BOP', 'CCI', 'CMO', 'DX', 'MACD', 'MACDEXT', 'MACDFIX', 'MFI', 'MINUS_DI', 'MINUS_DM', 'MOM',
'PLUS_DI', 'PLUS_DM', 'PPO', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'RSI', 'STOCH', 'STOCHF', 'STOCHRSI', 'TRIX', 'ULTOSC', 'WILLR', 'BBANDS', 'DEMA',
'EMA', 'HT_TRENDLINE', 'KAMA', 'MA', 'MAMA', 'MAVP', 'MIDPOINT', 'MIDPRICE', 'SAR', 'SAREXT', 'SMA', 'T3', 'TEMA', 'TRIMA', 'WMA', 'CDL2CROWS',
'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY', 'CDLADVANCEBLOCK',
'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 'CDLDOJISTAR',
'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER',
'CDLHANGINGMAN', 'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS', 'CDLINNECK',
'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW',
'CDLMATHOLD', 'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR', 'CDLONNECK', 'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS', 'CDLSEPARATINGLINES',
'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP', 'CDLTHRUSTING',
'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS', 'AVGPRICE', 'MEDPRICE', 'TYPPRICE', 'WCLPRICE', 'BETA', 'CORREL',
'LINEARREG', 'LINEARREG_ANGLE', 'LINEARREG_INTERCEPT', 'LINEARREG_SLOPE', 'STDDEV', 'TSF', 'VAR', 'ATR', 'NATR', 'TRANGE', 'AD', 'ADOSC', 'OBV']
"""
print(ta_list)

# df['k'], df['d'] = talib.STOCH(df['high'],
#                                df['low'],
#                                df['close'],
#                                fastk_period=9,
#                                slowk_period=3,
#                                slowd_period=3)

# df['k'], df['d'] = talib.STOCH(df['high'], df['low'], df['close'])

df['RSI'] = talib.RSI(df['close'], timeperiod=14)
df['k'], df['d'] = talib.STOCH(df['RSI'], df['RSI'], df['RSI'],
                               fastk_period=14, slowk_period=3,
                               slowk_matype=MA_Type.SMA,
                               slowd_period=3,
                               slowd_matype=MA_Type.SMA)

print(df.tail())

# """
# (MAVP)自由改變每一期計算移動平均的天數。比如說你有 90 天的資料,
#     ‧ 前面的 30 天想要計算 『5 日移動平均』
#     ‧ 中間的 30 天想要計算『 10 日移動平均』
#     ‧ 最後的 30 天想要計算『 20 日移動平均』
# """
# total = len(df.index)
# head_tail = int(total / 3)
# middle = total - (head_tail * 2)
#
# periods = []
# periods += head_tail * [5.0]
# periods += middle * [10.0]
# periods += head_tail * [20.0]
#
# df['periods'] = periods
#
# # 迴圈執行，看看結果吧！
# for x in ta_list:
#     try:
#         # x 為技術指標的代碼，透過迴圈填入，再透過 eval 計算出 output
#         output = eval('abstract.' + x + '(df)')
#         # 如果輸出是一維資料，幫這個指標取名為 x 本身；多維資料則不需命名
#         output.name = x.lower() if isinstance(output, pd.core.series.Series) else None
#         # 透過 merge 把輸出結果併入 df DataFrame
#         df = pd.merge(df, pd.DataFrame(output), left_on=df.index, right_on=output.index)
#         df = df.set_index('key_0')
#
#     except Exception as e:
#         print(f"Exception: {e}, {traceback.format_exc()}")
#         print(f"Exception: {x}")
#
# print(df)
