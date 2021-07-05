import csv
import inspect
import json
import os
import socket
import time
import traceback
import urllib
from urllib.request import urlopen

import pandas
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.collection_utils import CollectionUtils
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from projects.common.utils.date_utils import DateUtils

# 設置socket默認的等待時間，在read超時後能自動往下繼續跑
socket.setdefaulttimeout(10)


class FileUtils:

    @classmethod
    @interceptor
    def saveToOriginalHtml(cls, date: str):
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
        except requests.exceptions.ConnectionError as connError:
            log.warning(f"ConnectionError saveToOriginalHtml: {date}")
            CoreException.show_error(connError, traceback.format_exc())
            time.sleep(10)
            # (FIXME 觀察一陣子)使用[遞歸]重新進行，直到成功為止
            cls.saveToOriginalHtml(date)
        except Exception:
            raise
        finally:
            # Sleep in case the request is blocked
            time.sleep(6)

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
                soup = BeautifulSoup(open(filepath, "r", encoding="UTF-8"), "html.parser")
                # table = soup.findAll("table", {"class":"wikitable"})[0]
                table = soup.findAll("table")

                if not table:
                    log.warning(f"Table not exist, maybe there is no data on {date}")
                else:
                    table_last = table[len(table) - 1]
                    rows = table_last.findAll("tr")
                    # rows = table_9.findAll("tbody")

                    csv_filepath = (constants.CSV_PATH % date)
                    with open(csv_filepath, "w", newline="", encoding="UTF-8") as f:
                        writer = csv.writer(f)
                        for index, row in enumerate(rows):
                            csv_row = []

                            if not index == 1:
                                for cell in row.findAll(["td"]):
                                    csv_row.append(cell.get_text())
                                writer.writerow(csv_row)
        except Exception:
            raise

    @staticmethod
    @interceptor
    async def saveToFinalCsvAndReturnDf(date: str) -> DataFrame:
        """ Save final CSV and return pandas dataframe """
        log.debug(f"{inspect.currentframe().f_code.co_name}: {date}")

        try:
            # Empty dataFrame
            df = pandas.DataFrame()
            filepath = (constants.CSV_PATH % date)

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
            raise

    @staticmethod
    @interceptor
    def getDataDirect(date: str) -> DataFrame:
        """ Get data from CSV directly """
        try:
            # Empty dataFrame
            df = pandas.DataFrame()
            filepath = (constants.CSV_FINAL_PATH % date)

            if not os.path.isfile(filepath):
                log.warning(constants.DATA_NOT_EXIST % date)
            else:
                df = pandas.read_csv(filepath)
                new_headers = CollectionUtils.header_daily_stock(df[:1])
                df.columns = new_headers
                log.debug(df)
            return df
        except Exception:
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
            raise