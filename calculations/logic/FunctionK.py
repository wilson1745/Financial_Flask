# -*- coding: UTF-8 -*-
import datetime

from pandas import DataFrame

from calculations import log
from calculations.common.utils import constants
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo
from projects.common.utils.date_utils import DateUtils


# # BrokerID="capital" 、 "yuanta" 、 "kgi"
# @interceptor
# def getSIDMatch(Date, sid, BrokerID="capital", DataPath="C:/Data/"):
#     """
#     # 取得當月的日K
#     # 持續取得指定股票代碼的成交資訊
#     # 設定券商名稱
#     """
#     for i in tailer.follow(open(DataPath + BrokerID + "/" + Date + "/" + sid + "_Match.txt"), 0):
#         j = i.strip("\n").split(",")
#         yield j


# @interceptor
# def getLastSIDMatch(Date, sid, BrokerID="capital", DataPath="C:/Data/"):
#     """ 取得指定股票代碼的最新一筆成交資訊 """
#     tmpfiledata = open(DataPath + BrokerID + "/" + Date + "/" + sid + "_Match.txt").readlines()
#     tmpfiledata.reverse()
#     for i in tmpfiledata:
#         j = i.strip("\n").split(",")
#         return j


@interceptor
def getDayKBar(sid, yearmonth) -> DataFrame:
    """ 取得股票日Ｋ  """
    data = dailystock_repo.findMonthBySymbolAndYearMonth(sid, yearmonth)
    return data

    # # 透過API取得資料
    # html = urlopen("http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + date + "&stockNo=" + sid)
    # content = html.read().decode("utf-8")
    # jcontent = json.loads(content)
    # data = jcontent["data"]
    # # 將資料整理成可用的資訊
    # data = [[i[0], float(i[3].replace(",", "")), float(i[4].replace(",", "")), float(i[5].replace(",", "")),
    #          float(i[6].replace(",", "")), float(i[8].replace(",", ""))] for i in data]
    # return data


@interceptor
def getDayKBarbyNum(sid, daynum):
    """ 取得往前推算n日的日K """
    tmpday = DateUtils.today(constants.YYYYMM)

    # 首先取得當月資料
    dayK = getDayKBar(sid, tmpday)

    # 若資料數量不足，則更往前補足資料
    while len(dayK) < daynum:
        tmpday = (datetime.datetime.strptime((tmpday[:6] + "01"), constants.YYYYMMDD) - datetime.timedelta(
            days=1)).strftime(constants.YYYYMMDD)
        tmpdata = getDayKBar(sid, tmpday)
        dayK = tmpdata + dayK
        # time.sleep(3)

    # 回傳指定天數的日K
    return dayK[-daynum:]


# ------------------- App Test -------------------
if __name__ == "__main__":
    symbol = "2330"
    year_month = "202102"
    num = 5

    df = getDayKBar(symbol, year_month)
    # df = getDayKBarbyNum(symbol, num)
    log.debug(df)
