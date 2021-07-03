# -*- coding: UTF-8 -*-
import datetime

import numpy
import talib


class KBar:
    """
    - K線指標class
    - 參數 週期
    """

    def __init__(self, date, cycle=1):
        self.Cycle = datetime.timedelta(minutes=cycle)
        self.Time = datetime.datetime.strptime(date + '090000', '%Y%m%d%H%M%S') - (self.Cycle * 2)
        self.Open = numpy.array([])
        self.High = numpy.array([])
        self.Low = numpy.array([])
        self.Close = numpy.array([])
        self.Volume = numpy.array([])

    def Add(self, time, price, qty):
        """ 填入即時報價 """

        # 沒有換分鐘
        if time < self.Time + self.Cycle:
            self.Close[-1] = price
            self.Volume[-1] += qty
            if price > self.High[-1]:
                self.High[-1] = price
            elif price < self.Low[-1]:
                self.Low[-1] = price
            return 0
        # 穿越指定時間週期 新增一根K棒
        elif time >= self.Time + self.Cycle:
            while time >= self.Time + self.Cycle:
                self.Time += self.Cycle
            self.Open = numpy.append(self.Open, price)
            self.High = numpy.append(self.High, price)
            self.Low = numpy.append(self.Low, price)
            self.Close = numpy.append(self.Close, price)
            self.Volume = numpy.append(self.Volume, qty)
            return 1

    def GetOpen(self):
        """ 取得開盤價陣列 """
        return self.Open

    def GetHigh(self):
        """ 取得最高價陣列 """
        return self.High

    def GetLow(self):
        """ 取得最低價陣列 """
        return self.Low

    def GetClose(self):
        """ 取得收盤價陣列 """
        return self.Close

    def GetVolume(self):
        """ 取得累積成交量 """
        return self.Volume

    def GetSMA(self, tn=10):
        """ 取得移動平均線 """
        return talib.MA(self.Close, timeperiod=tn, matype=0)

    def GetQMA(self, tn=5):
        """ 取得量能移動平均 """
        return talib.MA(self.Volume, timeperiod=tn, matype=0)

    def GetMACD(self, fastp=12, slowp=24, signalp=7):
        """ 取得MACD """
        return talib.MACD(self.Close, fastperiod=fastp, slowperiod=slowp, signalperiod=signalp)

    def GetBBANDS(self, tp=10):
        """ 取得布林通道指標 """
        return talib.BBANDS(self.Close, timeperiod=tp, matype=0)

    def GetKD(self):
        """ 取得KD """
        return talib.STOCH(self.High, self.Low, self.Close)

    def GetWILLR(self, tp=14):
        """ 取得威廉指標 """
        return talib.WILLR(self.High, self.Low, self.Close, timeperiod=tp)

    def GetRSI(self, tp=14):
        """ 取得RSI """
        return talib.RSI(self.Close, timeperiod=tp)

    def GetBIAS(self, tn=10):
        """ 取得乖離率 """
        mavalue = talib.MA(self.Close, timeperiod=tn, matype=0)
        return (self.Close - mavalue) / mavalue


class BSPower1:
    """ 透過當前成交價 與上一筆成交價 相比計算內外盤 """

    def __init__(self):
        self.BP = 0
        self.SP = 0
        self.LastPrice = None

    def Add(self, price, qty):
        if self.LastPrice is None:
            self.LastPrice = price
        else:
            if price > self.LastPrice:
                self.BP += qty
            elif price < self.LastPrice:
                self.SP += qty
            self.LastPrice = price

    def Get(self):
        return [self.BP, self.SP]


class BSPower2:
    """ 透過當前成交價 與上下一檔價 相比計算內外盤 """

    def __init__(self):
        self.BP = 0
        self.SP = 0

    def Add(self, price, qty, ask, bid):
        if price >= bid:
            self.BP += qty
        elif price <= ask:
            self.SP += qty

    def Get(self):
        return [self.BP, self.SP]
