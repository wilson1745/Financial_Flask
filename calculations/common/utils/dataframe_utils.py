# -*- coding: UTF-8 -*-
import csv

import pandas as pd
from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import CLOSE, CLOSE_PRICE, CREATETIME, DEAL_PRICE, DEAL_STOCK, HEADERS, HIGH, HIGHEST_PRICE, LOW, \
    LOWEST_PRICE, MARKET_DATE, OPEN, OPENING_PRICE, STOCK_NAME, SYMBOL, UPS_AND_DOWNS
from calculations.core.Interceptor import interceptor

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


class DataFrameUtils:

    # def __init__(self):
    # """ FIXME Constructor """
    # pd.set_option("display.width", None)
    # pd.set_option('display.max_colwidth', None)
    # pd.set_option("display.max_columns", None)
    # pd.set_option("display.max_rows", None)
    # pd.set_option("display.unicode.ambiguous_as_wide", True)
    # pd.set_option("display.unicode.east_asian_width", True)

    @staticmethod
    @interceptor
    def arrangeMiIndex(rows) -> list:
        """ 處理爬蟲完的資料 """
        data_row = []

        # 以迴圈輸出每一列
        index = 0
        for row in rows:
            if index > 205:
                data_row.append(row)
            index = index + 1

        for row in data_row:
            row[0] = row[0].replace('=', '')
            row[0] = row[0].replace('"', '')
            row[2] = row[2].replace(',', '')
            row[3] = row[3].replace(',', '')
            row[4] = row[4].replace(',', '')
            row[5] = row[5].replace(',', '')
            row[6] = row[6].replace(',', '')
            row[7] = row[7].replace(',', '')
            row[8] = row[8].replace(',', '')
            row[5] = row[5].replace('--', '0')
            row[6] = row[6].replace('--', '0')
            row[7] = row[7].replace('--', '0')
            row[8] = row[8].replace('--', '0')

            if row[9] and row[9] == '-':
                if row[10] and row[10] != '0':
                    row[10] = row[9] + row[10]
            # print(row)

        return data_row

    @staticmethod
    @interceptor
    def arrangeMiIndexHtml(rows) -> list:
        """ 處理爬蟲完的資料 """
        data_row = []

        # 以迴圈輸出每一列
        index = 0
        for row in rows:
            if index > 1:
                data_row.append(row)
            index = index + 1

        for row in data_row:
            row[0] = row[0].replace('=', '')
            row[0] = row[0].replace('"', '')
            row[2] = row[2].replace(',', '')
            row[3] = row[3].replace(',', '')
            row[4] = row[4].replace(',', '')
            row[5] = row[5].replace(',', '')
            row[6] = row[6].replace(',', '')
            row[7] = row[7].replace(',', '')
            row[8] = row[8].replace(',', '')
            row[5] = row[5].replace('--', '0')
            row[6] = row[6].replace('--', '0')
            row[7] = row[7].replace('--', '0')
            row[8] = row[8].replace('--', '0')

            if row[9] and row[9] == '-':
                if row[10] and row[10] != '0':
                    row[10] = row[9] + row[10]
            # print(row)

        return data_row

    @classmethod
    @interceptor
    def arrangeHtmlToDataFrame(cls, rows, date) -> DataFrame:
        """ 處理爬蟲完的資料 """
        try:
            data_row = cls.arrangeMiIndexHtml(rows)

            # FIXME 這寫法有點笨...
            dataFrame = pd.DataFrame(data_row)
            dataFrame.drop([9, 11, 12, 13, 14, 15], axis=1, inplace=True)

            dataFrame.astype(object).where(pd.notnull(dataFrame), None)
            dataFrame.fillna(0, inplace=True)

            # 塞入第一欄[日期] (market_date)
            dataFrame.insert(0, HEADERS[0], date)
            # log.debug(f"df.columns: {dataFrame.columns}")

            # 先儲存CSV
            dataFrame.columns = HEADERS
            # df.to_csv((CSV_FINAL_PATH % date), index=False, header=True)
            # df.columns = CollectionUtils.header_daily_stock(HEADERS)
            log.debug(dataFrame)

            return dataFrame
        except Exception:
            raise

    @staticmethod
    @interceptor
    def listDataRows(filepath):
        try:
            with open(filepath, encoding="utf-8", errors="ignore") as csvfile:
                # 讀取 CSV 檔案內容
                rows = csv.reader(csvfile)

                # 以迴圈輸出每一列
                for row in rows:
                    log.debug(row)
        except Exception:
            raise

    @staticmethod
    @interceptor
    def dfForTalib(df: DataFrame) -> DataFrame:
        try:
            df = df.drop([MARKET_DATE, STOCK_NAME, SYMBOL, DEAL_STOCK, DEAL_PRICE, UPS_AND_DOWNS, CREATETIME], axis=1)
            df = df.rename(columns={OPENING_PRICE: OPEN, HIGHEST_PRICE: HIGH, LOWEST_PRICE: LOW, CLOSE_PRICE: CLOSE})
            return df
        except Exception:
            raise
