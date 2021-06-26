# 一分鐘K棒的物件
from datetime import datetime

from calculations.logic import FunctionMA, indicator
from calculations.repository import dailystock_repo

# 取得當天日期
Date = datetime.now().strftime("%Y%m%d")

# 測試股票下單
Sid = "2330"

# 一分鐘K棒的物件
KBar1M = indicator.KBar(date=Date)

# 定義RSI指標、快線、慢線的週期
RSIPeriod = 14
FastPeriod = 5
SlowPeriod = 15

# 進場判斷
df = dailystock_repo.findBySymbol(Sid)

df = FunctionMA.GetCross(df, FastPeriod, SlowPeriod)

# df['ma5'] = df['close_price'].rolling(window=5, center=False).mean()
# df['ma15'] = df['close_price'].rolling(window=15, center=False).mean()
#
# # 删除空值
# # df = df.dropna()

# # 持仓情况
# df['pos'] = 0  # 初始化
#
# # 交易信号判断
# df['pos'][df[f'ma{FastPeriod}'] >= df[f'ma{SlowPeriod}']] = 10000
# df['pos'][df[f'ma{FastPeriod}'] < df[f'ma{SlowPeriod}']] = -10000
# df['pos'] = df['pos'].shift(1).fillna(0)

print(df.tail(10))

# for i in data.values:
#     time = i['market_date']
#     price = i['close_price']
#     qty = i['volume']
#     check = KBar1M.Add(time, price, qty)
#
# HEADERS = ["market_date", "stock_name", "symbol", "deal_stock", "deal_price", "opening_price", "highest_price",
#            "lowest_price", "close_price", "ups_and_downs", "volume", "createtime"]

# Index = 0
#
# for i in function.getSIDMatch(Date, Sid):
#     time = datetime.strptime(Date + i[0], '%Y%m%d%H:%M:%S.%f')
#     price = float(i[2])
#     qty = int(i[3])
#     check = KBar1M.Add(time, price, qty)
#
#     RSI = KBar1M.GetRSI(RSIPeriod)
#     SlowMA = KBar1M.GetSMA(SlowPeriod)
#     # 當RSI指標及慢線皆已計算完成，才會去進行判斷
#     if len(RSI) >= RSIPeriod and len(SlowMA) >= SlowPeriod + 1:
#         RSI = RSI[-1]
#         FastMA = KBar1M.GetSMA(FastPeriod)
#         ThisFastMA = FastMA[-1]
#         ThisSlowMA = SlowMA[-1]
#         LastFastMA = FastMA[-2]
#         LastSlowMA = SlowMA[-2]
#
#         # RSI指標趨勢偏多且均線黃金交叉
#         if RSI > 50 and LastFastMA <= LastSlowMA and ThisFastMA > ThisSlowMA:
#             Index = 1
#             OrderTime = time
#             OrderPrice = price
#             print(OrderTime, "Order Buy Price:", OrderPrice, "Success!")
#             break
#         # RSI指標趨勢偏空且均線死亡交叉
#         elif RSI < 50 and LastFastMA >= LastSlowMA and ThisFastMA < ThisSlowMA:
#             Index = -1
#             OrderTime = time
#             OrderPrice = price
#             print(OrderTime, "Order Sell Price:", OrderPrice, "Success!")
#             break
