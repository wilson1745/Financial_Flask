# -- coding:utf-8 --

import datetime as datetime

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas_datareader as pdr
from fbprophet import Prophet
from sklearn import metrics

pd.set_option("display.width", 320)
pd.set_option("display.max_columns", 20)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)

# 讀取股票
start = datetime.datetime(2015, 1, 5)
# df_2492 = pdr.DataReader('2492.TW', 'yahoo', start=start)
# df_2492 = pdr.DataReader('2330.TW', 'yahoo', start=start)
df_2492 = pdr.DataReader('2617.TW', 'yahoo', start=start)
print(f"df_2492.head(): {df_2492.head()}")

# 收盤價
plt.style.use('ggplot')
df_2492['Adj Close'].plot(figsize=(12, 8))

# 使用Prophet來預測股票
new_df_2492 = pd.DataFrame(df_2492['Adj Close']).reset_index().rename(columns={'Date': 'ds', 'Adj Close': 'y'})
print(f"new_df_2492: {new_df_2492.head()}")

new_df_2492['y'] = np.log(new_df_2492['y'])
print(f"np.log new_df_2492: {new_df_2492.head()}")
# 定義模型
model = Prophet()

# 訓練模型
model.fit(new_df_2492)

# 建構預測集 (forecasting for 1 year from now.)
future = model.make_future_dataframe(periods=365)

# 進行預測
forecast = model.predict(future)
print(f"forecast: {forecast}")

# 黑色代表實際的值，請注意黑色只到今天這個日期，藍線代表的是預測值，而淡藍色的陰影區表示不確定性，未來時間距離越遠，不確定區域就會越來越大。
figure = model.plot(forecast)

# 如果不考慮未來的不確定性，只有看預測和實際數據的最後800筆(一年252筆)，只想看實際和預測之間的視覺差距。橘色是實際的股價，藍色是預測的股價
df_2492_close = pd.DataFrame(df_2492['Adj Close'])
two_years = forecast.set_index('ds').join(df_2492_close)
two_years = two_years[['Adj Close', 'yhat', 'yhat_upper', 'yhat_lower']].dropna().tail(800)
two_years['yhat'] = np.exp(two_years.yhat)
two_years['yhat_upper'] = np.exp(two_years.yhat_upper)
two_years['yhat_lower'] = np.exp(two_years.yhat_lower)
two_years[['Adj Close', 'yhat']].plot(figsize=(8, 6))

# 計算誤差 => 計算實際的股價和預測股價的誤差
two_years_AE = (two_years.yhat - two_years['Adj Close'])
two_years_AE.describe()

# MSE：均方誤差 => MSE越接近0越好
print("MSE:", metrics.mean_squared_error(two_years.yhat, two_years['Adj Close']))

# MAE：平均絕對誤差
print("MAE:", metrics.mean_absolute_error(two_years.yhat, two_years['Adj Close']))

fig, ax1 = plt.subplots(figsize=(10, 8))
ax1.plot(two_years['Adj Close'])
ax1.plot(two_years.yhat)
ax1.plot(two_years.yhat_upper, color='black', linestyle=':', alpha=0.5)
ax1.plot(two_years.yhat_lower, color='black', linestyle=':', alpha=0.5)

# 橘色是實際的價格，藍色是是預測的，上下限用灰色。除了2018年7月的時候波動性太大造成的預測比較不準外，其他其實都蠻相近的。
ax1.set_title('華新科技實際和預測的誤差')
ax1.set_ylabel('Price')
ax1.set_xlabel('Date')

matplotlib.matplotlib_fname()

plt.show()
