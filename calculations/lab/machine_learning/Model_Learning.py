""" Do not delete import (from talib import abstract) """
import datetime as dt
import os
import traceback

import graphviz
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame
from sklearn.metrics import auc, confusion_matrix, roc_curve
from sklearn.tree import DecisionTreeClassifier, export_graphviz

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.repository import dailystock_repo
from talib import abstract

if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    try:
        symbol = "6116"
        start = "20210101"
        end = "20210504"
        # end = DateUtils.today(Constants.YYYYMMDD)
        filePath = f"./files/{symbol}_{DateUtils.today(constants.YYYYMMDD)}"

        # df: DataFrame = dailystock_repo.findBySymbol(symbol)
        df: DataFrame = dailystock_repo.findBySymbolAndMarketWithRange(symbol, start, end)
        df = df.drop(["market_date", "stock_name", "symbol", "deal_stock", "deal_price", "ups_and_downs", "createtime"], axis=1)
        df = df.rename(columns={"opening_price": "open", "highest_price": "high", "lowest_price": "low", "close_price": "close"})
        # print(data)

        ta_list = ["MACD", "RSI", "MOM", "STOCH"]

        """ Abstract API 1 """
        for x in ta_list:
            output = eval("abstract." + x + "(df)")
            output.name = x.lower() if isinstance(output, pd.core.series.Series) else None
            df = pd.merge(df, pd.DataFrame(output), left_on=df.index, right_on=output.index)
            df = df.set_index("key_0")

        """ Abstract API 2 """
        # df["RSI"] = abstract.RSI(data)
        # df["SMA"] = abstract.SMA(data, 5)
        # df["ADX"] = abstract.ADX(data, timperiod=14)

        """ Function API """
        # output = talib.RSI(df["close"])
        # output.name = "RSI" if type(output) == pd.core.series.Series else None
        # df = pd.merge(df, pd.DataFrame(output), left_on=data.index, right_on=output.index)
        # df = df.set_index("key_0")

        # log.debug(data)

        """
        標記預測目標：預測一週後（五交易日後）收盤價相對今日收盤價是漲或跌 (五日後漲標記 1，反之標記 0)
        1. 漲：五交易日後的收盤價，比今日收盤價高
        2. 跌：五交易日後的收盤價，比今日收盤價低
        """
        df["week_trend"] = np.where(df.close.shift(-5) > df.close, 1, 0)
        # log.debug(df["week_trend"])

        # TODO
        """
        目標進行視覺化 => 這就是我們希望 A.I. 能夠做出的預測
        1. 紅色區塊 = 五日後 → 漲
        2. 綠色區塊 = 五日後 → 跌
        """
        # 按日統計的數據通過降採樣的方法
        df = df.resample(rule="D").ffill()
        # log.debug(df)

        t = mdates.drange(df.index[0], df.index[-1], dt.timedelta(hours=24))
        y = np.array(df.close[:-1])

        fig, ax = plt.subplots()

        ax.plot_date(t, y, "b-")
        for i in range(len(df)):
            if df.week_trend[i] == 1:
                ax.axvspan(
                    mdates.datestr2num(df.index[i].strftime(constants.YYYYMMDD_LINE)) - 0.5,
                    mdates.datestr2num(df.index[i].strftime(constants.YYYYMMDD_LINE)) + 0.5,
                    facecolor="red", edgecolor="none", alpha=0.5
                )
            else:
                ax.axvspan(
                    mdates.datestr2num(df.index[i].strftime(constants.YYYYMMDD_LINE)) - 0.5,
                    mdates.datestr2num(df.index[i].strftime(constants.YYYYMMDD_LINE)) + 0.5,
                    facecolor="green", edgecolor="none", alpha=0.5
                )

        fig.autofmt_xdate()
        fig.set_size_inches(20, 10.5)
        fig.savefig(filePath + ".png")
        # plt.show()

        # TODO
        """
        資料預處理
        1. 缺值的處理：『要處理』，技術指標中存在 nan 值
        2. 類別數據的處理：『不須處理』，這次數據資料中並無類別數據
        3. 數據標準化：『不須處理』，決策樹可以不用執行標準化
        """
        # 檢查資料有無缺值
        # df.isnull().sum()
        # 最簡單的作法是把有缺值的資料整列拿掉
        learnData = df.dropna()

        # TODO
        """
        學習/測試樣本切割
        """
        # 決定切割比例為 70%:30%
        split_point = int(len(learnData) * 0.7)

        # 切割成學習樣本以及測試樣本 => 捨棄最後5筆為預測目標是 5 日後的漲跌
        train = learnData.iloc[:split_point, :].copy()
        test = learnData.iloc[split_point:-5, :].copy()

        # 訓練樣本再分成目標序列 y 以及因子矩陣 X
        train_X = train.drop("week_trend", axis=1)
        train_y = train.week_trend

        # 測試樣本再分成目標序列 y 以及因子矩陣 X
        test_X = test.drop("week_trend", axis=1)
        test_y = test.week_trend

        """ 讓 A.I. 學習->改正->測驗 """
        # 宣告一棵決策樹
        model = DecisionTreeClassifier(max_depth=7)

        # 讓 A.I. 學習
        model.fit(train_X, train_y)

        # 讓 A.I. 測驗，prediction 存放了 A.I. 根據測試集做出的預測
        prediction = model.predict(test_X)

        # 視覺化這棵樹
        dot_data = export_graphviz(model, out_file=None,
                                   feature_names=train_X.columns,
                                   filled=True, rounded=True,
                                   class_names=True,
                                   special_characters=True)
        graph = graphviz.Source(dot_data)
        graph.render(filename=filePath + "_decision_tree")

        """ 測驗結果分析 """
        # 混淆矩陣
        matrix = confusion_matrix(test_y, prediction)
        log.debug(f"confusion_matrix(test_y, prediction): {matrix}")
        # 準確率
        score = model.score(test_X, test_y)
        log.debug(f"model.score(test_X, test_y): {score}")

        # 計算 ROC 曲線
        false_positive_rate, true_positive_rate, thresholds = roc_curve(test_y, prediction)
        # 計算 AUC 面積
        area = auc(false_positive_rate, true_positive_rate)
        log.debug(f"auc(false_positive_rate, true_positive_rate): {area}")

        """ 透過 AUC，決定決策樹深度的最佳參數 """
        maxAUC: float = 0
        maxDepth = 0

        # 測試一批深度參數，一般而言深度不太會超過 3x，我們這邊示範 1 到 50 好了
        depth_parameters = np.arange(1, 50)
        # 準備兩個容器，一個裝所有參數下的訓練階段 AUC；另一個裝所有參數下的測試階段 AUC
        train_auc = []
        test_auc = []

        # 根據每一個參數跑迴圈
        for test_depth in depth_parameters:
            # 根據該深度參數，創立一個決策樹模型，取名 temp_model
            temp_model = DecisionTreeClassifier(max_depth=test_depth)
            # 讓 temp_model 根據 train 學習樣本進行學習
            temp_model.fit(train_X, train_y)
            # 讓學習後的 temp_model 分別根據 train 學習樣本以及 tests 測試樣本進行測驗
            train_predictions = temp_model.predict(train_X)
            test_predictions = temp_model.predict(test_X)
            # 計算學習樣本的 AUC，並且紀錄起來
            false_positive_rate, true_positive_rate, thresholds = roc_curve(train_y, train_predictions)
            auc_area = auc(false_positive_rate, true_positive_rate)
            train_auc.append(auc_area)
            # 計算測試樣本的 AUC，並且紀錄起來
            false_positive_rate, true_positive_rate, thresholds = roc_curve(test_y, test_predictions)
            auc_area = auc(false_positive_rate, true_positive_rate)
            test_auc.append(auc_area)

            # 紀錄最高值的AUC
            if maxAUC < auc_area:
                maxAUC = auc_area
                maxDepth = test_depth

        log.debug(f"maxAUC: {maxAUC}")
        log.debug(f"maxDepth: {maxDepth}")

        # 繪圖視覺化
        plt.figure(figsize=(14, 10))
        plt.plot(depth_parameters, train_auc, "b", label="Train AUC")
        plt.plot(depth_parameters, test_auc, "r", label="Test AUC")
        plt.ylabel("AUC")
        plt.xlabel("depth parameter")
        """ zip joins x and y coordinates in pairs """
        # for x, y in zip(depth_parameters, test_auc):
        #     label = "{:.2f}".format(y)
        #     plt.annotate(label,  # this is the text
        #                  (x, y),  # this is the point to label
        #                  textcoords="offset points",  # how to position the text
        #                  xytext=(0, 10),  # distance from text to points (x,y)
        #                  ha='center')  # horizontal alignment can be left, right or center
        plt.show()

    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        log.info(f"====== End of {os.path.basename(__file__)} ======")
