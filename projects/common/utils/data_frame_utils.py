import csv
import logging
import traceback

import pandas as pd
from pandas import DataFrame

from projects.common import constants
from projects.common.exceptions.core_exception import CoreException
from projects.common.interceptor import interceptor

log = logging.getLogger(constants.LOG_PROJECTS)

pd.set_option('display.width', 320)
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', None)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

HEADERS = ['market_date', 'stock_name', 'symbol', 'deal_stock', 'deal_price', 'opening_price', 'highest_price',
           'lowest_price', 'close_price', 'ups_and_downs', 'volume', 'createtime']


class DataFrameUtils:

    @staticmethod
    @interceptor
    def arrangeMiIndex(rows) -> list:
        """ 處理爬蟲完的資料 """
        try:
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
        except Exception:
            raise

    @staticmethod
    @interceptor
    def arrangeMiIndexHtml(rows) -> list:
        """ 處理爬蟲完的資料 """
        try:
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
        except Exception:
            raise

    @classmethod
    @interceptor
    def arrangeHtmlToDataFrame(cls, rows, date) -> DataFrame:
        """ 處理爬蟲完的資料 """
        try:
            data_row = cls.arrangeMiIndexHtml(rows)

            # FIXME 這寫法有點笨...
            df = pd.DataFrame(data_row)
            df.drop([9, 11, 12, 13, 14, 15], axis=1, inplace=True)

            df.astype(object).where(pd.notnull(df), None)
            df.fillna(0, inplace=True)

            # 塞入第一欄[日期] (market_date)
            df.insert(0, constants.HEADERS[0], date)
            # log.debug(f'df.columns: {dataFrame.columns}')

            # 先儲存CSV
            df.columns = constants.HEADERS
            # df.to_csv((CSV_FINAL_PATH % date), index=False, header=True)
            # df.columns = CollectionUtils.header_daily_stock(HEADERS)
            log.debug(df)

            return df
        except Exception:
            raise

    @staticmethod
    @interceptor
    def listDataRows(filepath):
        """ Review file data """
        try:
            with open(filepath, encoding='utf-8', errors='ignore') as csvfile:
                # 讀取 CSV 檔案內容
                rows = csv.reader(csvfile)

                # 以迴圈輸出每一列
                for row in rows:
                    log.debug(row)
        except Exception:
            raise

    @staticmethod
    @interceptor
    def genDataFrame(datas: list) -> DataFrame:
        """ Generate pandas dataframe """
        try:
            df = pd.DataFrame(datas)
            if df.empty:
                log.warning('No data exist!')
            else:
                df.columns = HEADERS
                df.index = pd.to_datetime(df['market_date'])
                log.debug(df)

            return df
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            raise e
