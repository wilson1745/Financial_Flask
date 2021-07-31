# -*- coding: UTF-8 -*-
import csv
import multiprocessing
import traceback
from multiprocessing.pool import ThreadPool, ThreadPool as Pool

import pandas as pd
from pandas import DataFrame

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.constants import CLOSE, CREATETIME, DEAL_PRICE, DEAL_STOCK, HEADER_ITEMFUND_E, HEADERS, HEADERS_DF_E, HEADERS_T, \
    HIGH, LOW, MARKET_DATE, STOCK_NAME, SYMBOL, UPS_AND_DOWNS, UPS_AND_DOWNS_PCT
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


class DataFrameUtils:
    """ TODO add description """

    def __init__(self):
        """ Constructor """
        pass

    @staticmethod
    @interceptor
    def __industryRow(row):
        """ 處理爬蟲完的資料 (Industry) """
        if row:
            row[0] = row[0].replace('--', '0')
            row[1] = row[1].replace('--', '0')
            row[3] = row[3].replace('--', '0')
            row[4] = row[4].replace('--', '0')
            row[1] = row[1].replace(',', '')
            row[3] = row[3].replace(',', '')

            if row[2] and row[2] == '-':
                if row[3] and row[3] != '0':
                    row[3] = row[2] + row[3]
                # log.debug(row)
            return row
        else:
            log.warning(constants.DATA_NOT_EXIST % row)
            return None

    @staticmethod
    @interceptor
    def __dailys_tock_row(row):
        """ 處理爬蟲完的資料 (DailyStock) """
        if row:
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
                # log.debug(row)
        else:
            log.warning(constants.DATA_NOT_EXIST % row)

    @classmethod
    @interceptor
    def __arrangeMiIndexHtml(cls, rows: list) -> list:
        """ 處理爬蟲完的資料 """
        data_row = []

        # 輸出每一列(刪除前2行的資訊)
        for index, row in enumerate(rows):
            # log.debug(f"{index}: {value}")
            if index > 1:
                data_row.append(row)
        # data_row = rows[2:]

        pools = ThreadPool(multiprocessing.cpu_count() - 1)
        pools.map(func=cls.__dailys_tock_row,
                  iterable=data_row)

        return data_row

    @classmethod
    @interceptor
    def arrangeHtmlToDataFrame(cls, rows, date) -> DataFrame:
        """ 處理爬蟲完的資料 """
        try:
            # df = pd.DataFrame()
            #
            # processPools = Pool(multiprocessing.cpu_count() - 1)
            # results = processPools.map_async(func=cls.__arrangeMiIndexHtml,
            #                                  iterable=rows[2:],
            #                                  callback=CoreException.show,
            #                                  error_callback=CoreException.error)

            data_row = cls.__arrangeMiIndexHtml(rows)

            # FIXME 這寫法有點笨...
            df = pd.DataFrame(data_row)
            df.drop([9, 11, 12, 13, 14, 15], axis=1, inplace=True)

            df.astype(object).where(pd.notnull(df), None)
            df.fillna(0, inplace=True)

            # 塞入第一欄[日期] (market_date)
            df.insert(0, HEADERS[0], date)
            # log.debug(f"df.columns: {dataFrame.columns}")

            # 先儲存CSV
            df.columns = HEADERS
            # log.debug(df)

            return df
        except Exception:
            raise

    @classmethod
    @interceptor
    def genIndustryDf(cls, industry_rows: list) -> DataFrame:
        """ 處理爬蟲完的資料(價格指數) """
        try:
            # Empty dataFrame
            df = pd.DataFrame()

            pools = Pool(multiprocessing.cpu_count() - 1)
            results = pools.map(func=cls.__industryRow, iterable=industry_rows)

            if len(results) > 0:
                df = pd.DataFrame(results)
                # FIXME 這寫法有點笨...
                df.drop([2, 5], axis=1, inplace=True)
                df.columns = constants.HEADER_INDEX_E

                # Convert dtype
                df[[UPS_AND_DOWNS, UPS_AND_DOWNS_PCT]] = df[[UPS_AND_DOWNS, UPS_AND_DOWNS_PCT]].apply(pd.to_numeric)

                # Sort by column
                df = df.sort_values(by=[UPS_AND_DOWNS_PCT], axis=0, ascending=False)
                # log.debug(df)

            return df
        except Exception:
            raise

    @staticmethod
    @interceptor
    def list_rows(filepath):
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
            """ 寫法保留：df欄位變換名稱用 """
            # df = df.rename(columns={OPENING_PRICE: OPEN, HIGHEST_PRICE: HIGH, LOWEST_PRICE: LOW, CLOSE_PRICE: CLOSE})
            return df
        except Exception:
            raise

    @classmethod
    @interceptor
    def gen_stock_df(cls, rows: list) -> DataFrame:
        """ Generate pandas dataframe """
        try:
            df = pd.DataFrame(rows)
            if df.empty:
                log.warn("No data exist!")
            else:
                df.columns = HEADERS_T
                df.index = pd.to_datetime(df['market_date'])
                # log.debug(df)
            return df
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            raise e

    @classmethod
    @interceptor
    def gen_item_df(cls, rows: list) -> DataFrame:
        """ Generate pandas dataframe """
        try:
            df = pd.DataFrame(rows)
            if df.empty:
                log.warn('No data exist!')
            else:
                df.columns = HEADER_ITEMFUND_E
                df.index = df['symbol']
                # log.debug(df)
            return df
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            raise e

    @classmethod
    @interceptor
    def gen_fund_df(cls, rows) -> DataFrame:
        """ 處理(基金)爬蟲完的資料 """
        df = pd.DataFrame(rows)
        if df.empty:
            log.warn("No data exist!")
        else:
            df.columns = HEADERS_DF_E
            df = df.set_index(df[MARKET_DATE])
            # 計算各種指標使用
            df[LOW] = df[CLOSE]
            df[HIGH] = df[CLOSE]
        return df
