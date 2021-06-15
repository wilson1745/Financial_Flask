import csv
import inspect
import json
import os
import socket
import urllib
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pandas
from bs4 import BeautifulSoup
from pandas import DataFrame

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.collection_utils import CollectionUtils
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.core.Interceptor import interceptor
from projects.common.utils.date_utils import DateUtils

# 設置socket默認的等待時間，在read超時後能自動往下繼續跑
socket.setdefaulttimeout(10)


class FileUtils:

    @staticmethod
    @interceptor
    def saveToOriginalHtml(date: str):
        """ Get HTML from [www.twse.com.tw] """
        # log.debug(f"{inspect.currentframe().f_code.co_name}: {date}")
        log.debug(f"saveToOriginalHtml: {date}")

        try:
            html_path = (constants.HTML_PATH % date)

            """ 不管如何都儲存成html檔 => 證交所2pm才會有當天資料 """
            # ex: url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date={date}&type=ALLBUT0999"
            url = (constants.TWSE_MI_INDEX % ("html", date, "ALLBUT0999"))
            log.debug(f"Url: {url}")

            response = urllib.request.urlopen(url, timeout=60)
            webContent = response.read()

            f = open(html_path, "wb")
            f.write(webContent)
            f.close()

            """ 使用urlopen方法太過頻繁，引起遠程主機的懷疑，被網站認定為是攻擊行為。導致urlopen()後，request.read()一直卡死在那裡。最後拋出10054異常。 """
            response.close()
        except HTTPError as e_http:
            log.error(f"HTTPError: {e_http}")
            # TODO Doing something like reactivate the program...

            raise e_http
        except URLError as e_url:
            log.error(f"URLError: {e_url}")
            # TODO Doing something like reactivate the program...

            raise e_url
        except Exception as e:
            log.error(f"Exception saveToOriginalHtml")
            raise e

    @staticmethod
    @interceptor
    async def saveToOriginalCsv(date: str):
        """ Save CSV """
        log.debug(f"saveToOriginalCsv: {date}")
        filepath = (constants.HTML_PATH % date)

        try:
            if not os.path.isfile(filepath):
                log.warning(constants.FILE_NOT_EXIST % filepath)
            else:
                log.debug(f"Reading {filepath}")

                soup = BeautifulSoup(open((constants.HTML_PATH % date), "r", encoding="UTF-8"), "html.parser")
                # table = soup.findAll("table", {"class":"wikitable"})[0]
                table = soup.findAll("table")

                if not table:
                    log.warning(f"Table not exist, maybe there is no data on {date}")
                else:
                    table_last = table[len(table) - 1]
                    rows = table_last.findAll("tr")
                    # rows = table_9.findAll("tbody")

                    filepath = (constants.CSV_PATH % date)
                    with open(filepath, "w", newline="", encoding="UTF-8") as f:
                        writer = csv.writer(f)
                        for index, row in enumerate(rows):
                            csv_row = []

                            if not index == 1:
                                for cell in row.findAll(["td"]):
                                    csv_row.append(cell.get_text())
                                writer.writerow(csv_row)

        except Exception:
            log.error(f"Exception saveToOriginalCsv")
            raise

    @staticmethod
    @interceptor
    async def saveToFinalCsvAndReturnDf(date: str) -> DataFrame:
        """ Save final CSV and return pandas dataframe """
        log.debug(f"{inspect.currentframe().f_code.co_name}: {date}")

        try:
            filepath = (constants.CSV_PATH % date)

            # Empty dataFrame
            df = pandas.DataFrame()

            if not os.path.isfile(filepath):
                log.warning(constants.FILE_NOT_EXIST % filepath)
            else:
                log.debug(f"Reading {filepath}")

                with open(filepath, errors="ignore", encoding="UTF-8") as csvfile:
                    # 讀取 CSV 檔案內容
                    rows = csv.reader(csvfile)

                    # 轉換html至csv格式的dataframe
                    df = DataFrameUtils.arrangeHtmlToDataFrame(rows, date)

                    # Save CSV file
                    df.to_csv((constants.CSV_FINAL_PATH % date), index=False, header=True)
                    df.columns = CollectionUtils.header_daily_stock(constants.HEADERS)

            return df
        except Exception:
            log.error(f"Exception saveToFinalCsvAndReturnDf")
            raise

    @staticmethod
    @interceptor
    async def saveCsvAndGetDf(date: str) -> DataFrame:
        """ Directly save final CSV and return pandas dataframe """
        log.debug(f"saveCsvGetDf: {date}")

        try:
            filepath = (constants.HTML_PATH % date)
            soup = BeautifulSoup(open(filepath, "r", encoding="UTF-8"), 'html.parser')
            table = soup.findAll('table')

            # Empty dataFrame
            df = pandas.DataFrame()

            if not table:
                # Can't find data in HTML file
                log.warning(f"{filepath} table not exist, no data on {date}")
            else:
                table_last = table[len(table) - 1]
                rows = table_last.findAll("tr")

                list_row = []
                for index, row in enumerate(rows):
                    # 設定一個array去接每個row
                    csv_row = []
                    if not index == 1:
                        for cell in row.findAll(["td"]):
                            csv_row.append(cell.get_text())
                        list_row.append(csv_row)
                # log.debug(list_row)

                # 處理html資料為pandas dataframe
                data_row = DataFrameUtils.arrangeMiIndexHtml(list_row)

                # FIXME 這寫法有點笨...
                df = pandas.DataFrame(data_row)
                df.drop([9, 11, 12, 13, 14, 15], axis=1, inplace=True)

                df.astype(object).where(pandas.notnull(df), None)
                df.fillna(0, inplace=True)

                # 塞入第一欄[日期] (market_date)
                df.insert(0, constants.HEADERS[0], date)
                log.debug(f"df.columns: {df.columns}")

                # 先儲存CSV
                df.columns = constants.HEADERS
                df.to_csv((constants.CSV_FINAL_PATH % date), index=False, header=True)
                # df.columns = CollectionUtils.header_daily_stock(constants.HEADERS)
                df.columns = CollectionUtils.header_daily_stock(df[:1])

                log.debug(df)

            return df
        except Exception:
            log.error(f"Exception saveCsvAndGetDf")
            raise

    @staticmethod
    @interceptor
    def getDataDirect(date: str) -> DataFrame:
        """ Get data from CSV directly """
        try:
            filepath = (constants.CSV_FINAL_PATH % date)

            # Empty dataFrame
            df = pandas.DataFrame()

            if not os.path.isfile(filepath):
                log.warning(constants.DATA_NOT_EXIST % date)
            else:
                df = pandas.read_csv(filepath)
                new_headers = CollectionUtils.header_daily_stock(df[:1])
                df.columns = new_headers
                log.debug(df)

            return df
        except Exception:
            log.error(f"Exception getDataDirect")
            raise

    @staticmethod
    @interceptor
    def genTxtFile(error_dates: list):
        """ Save txt file """
        try:
            filepath = constants.URL_ERROR_TXT_PATH % DateUtils.today(constants.YYYY_MM_DD)
            with open(filepath, "w") as output:
                output.write(json.dumps(error_dates))
        except Exception:
            log.error(f"Exception genTxtFile")
            raise

    @staticmethod
    @interceptor
    def readTxtFile(date: str):
        """ Read txt file """
        try:
            filepath = constants.URL_ERROR_TXT_PATH % DateUtils.today(constants.YYYY_MM_DD) if not date else date
            with open(filepath, errors="ignore", encoding="UTF-8") as output:
                content = json.loads(output.read())
                log.debug(f"row size: {len(content)}")
                log.debug(f"{content}")

            # FIXME return type?
            return content
        except Exception:
            log.error(f"Exception readTxtFile")
            raise
