import traceback

import pandas as pd
import talib
from pandas import DataFrame

from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.repository import dailystock_repo
from talib import abstract

pd.set_option('display.width', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

symbol = "2330"

df: DataFrame = dailystock_repo.findBySymbol(symbol)
df = DataFrameUtils.dfForTalib(df)

# 確認價量資料表 df 的值都是 float 格式
df = df.astype('float')

# 準備一份你想要計算並且併入 df 的技術指標清單
# ta_list = ['MACD', 'RSI']
# 這裡示範全部 158 種技術指標
ta_list = talib.get_functions()
print(ta_list)

""" 
(MAVP)自由改變每一期計算移動平均的天數。比如說你有 90 天的資料,
    ‧ 前面的 30 天想要計算 『5 日移動平均』
    ‧ 中間的 30 天想要計算『 10 日移動平均』
    ‧ 最後的 30 天想要計算『 20 日移動平均』 
"""
total = len(df.index)
head_tail = int(total / 3)
middle = total - (head_tail * 2)

periods = []
periods += head_tail * [5.0]
periods += middle * [10.0]
periods += head_tail * [20.0]

df['periods'] = periods

# 迴圈執行，看看結果吧！
for x in ta_list:
    try:
        # x 為技術指標的代碼，透過迴圈填入，再透過 eval 計算出 output
        output = eval('abstract.' + x + '(df)')
        # 如果輸出是一維資料，幫這個指標取名為 x 本身；多維資料則不需命名
        output.name = x.lower() if isinstance(output, pd.core.series.Series) else None
        # 透過 merge 把輸出結果併入 df DataFrame
        df = pd.merge(df, pd.DataFrame(output), left_on=df.index, right_on=output.index)
        df = df.set_index('key_0')

    except Exception as e:
        print(f"Exception: {e}, {traceback.format_exc()}")
        print(f"Exception: {x}")

print(df)
