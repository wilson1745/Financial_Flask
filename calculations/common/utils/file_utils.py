import csv
import inspect
import json
import os
import re
import socket
import time
import traceback
import urllib
from datetime import datetime
from urllib.error import URLError
from urllib.request import urlopen

import pandas
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame

from calculations import LOG
from calculations.common.utils import constants
from calculations.common.utils.collection_utils import CollectionUtils
from calculations.common.utils.constants import CLOSE, HEADERS_DF, HTML_PATH, TWSE_MI_INDEX, UPS_AND_DOWNS
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from projects.common.utils.date_utils import DateUtils

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)

# 設置socket默認的等待時間，在read超時後能自動往下繼續跑
socket.setdefaulttimeout(10)


class FileUtils:
    """ TODO description """

    @classmethod
    @interceptor
    def save_to_original_html(cls, date: str):
        """ Get HTML from [www.twse.com.tw] """
        # log.debug(f"{inspect.currentframe().f_code.co_name}: {date}")
        LOG.debug(f"saveToOriginalHtml: {date}")

        try:
            """ 不管如何都儲存成html檔 => 證交所2pm才會有當天資料 """
            # ex: url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date={date}&type=ALLBUT0999"
            html_path = (HTML_PATH % date)
            url = (TWSE_MI_INDEX % ("html", date, "ALLBUT0999"))
            LOG.debug(f"Url: {url}")

            response = urlopen(url, timeout=60)
            webContent = response.read()

            f = open(html_path, "wb")
            f.write(webContent)
            f.close()

            """ 使用urlopen方法太過頻繁，引起遠程主機的懷疑，被網站認定為是攻擊行為。導致urlopen()後，request.read()一直卡死在那裡。最後拋出10054異常。 """
            response.close()
        except requests.exceptions.ConnectionError as connError:
            LOG.warning(f"ConnectionError saveToOriginalHtml: {date}")
            CoreException.show_error(connError, traceback.format_exc())
            time.sleep(10)
            # (FIXME 觀察一陣子)使用[遞歸]重新進行，直到成功為止
            cls.save_to_original_html(date)
        except URLError as urlError:
            LOG.error(f"__get_response URLError: {urlError}")
            CoreException.show_error(urlError, traceback.format_exc())
            time.sleep(10)
            cls.save_to_original_html(date)
        except Exception:
            raise
        finally:
            # Sleep in case the request is blocked
            time.sleep(6)

    @staticmethod
    @interceptor
    def save_to_original_csv(date: str):
        """ Save CSV """
        LOG.debug(f"saveToOriginalCsv: {date}")
        filepath = (constants.HTML_PATH % date)

        if not os.path.isfile(filepath):
            LOG.warning(constants.FILE_NOT_EXIST % filepath)
        else:
            LOG.debug(f"Reading {filepath}")
            soup = BeautifulSoup(open(filepath, 'r', encoding='UTF-8'), 'html.parser')
            # table = soup.findAll("table", {"class":"wikitable"})[0]
            table = soup.findAll('table')

            if not table:
                LOG.warning(f"Table not exist, maybe there is no data on {date}")
            else:
                table_last = table[len(table) - 1]
                rows = table_last.find_all('tr')
                # rows = table_9.findAll("tbody")

                csv_filepath = (constants.CSV_PATH % date)
                with open(csv_filepath, 'w', newline='', encoding='UTF-8') as f:
                    writer = csv.writer(f)
                    for index, row in enumerate(rows):
                        csv_row = []

                        if not index == 1:
                            for cell in row.find_all(['td']):
                                csv_row.append(cell.get_text())
                            writer.writerow(csv_row)

    @staticmethod
    @interceptor
    def save_to_final_csv_return_df(date: str) -> DataFrame:
        """ Save final CSV and return pandas dataframe """
        LOG.debug(f"{inspect.currentframe().f_code.co_name}: {date}")

        # Empty dataFrame
        df = pandas.DataFrame()
        filepath = (constants.CSV_PATH % date)

        if not os.path.isfile(filepath):
            LOG.warning(constants.FILE_NOT_EXIST % filepath)
        else:
            LOG.debug(f"Reading {filepath}")
            with open(filepath, errors='ignore', encoding='UTF-8') as csvfile:
                # 讀取 CSV 檔案內容
                rows = csv.reader(csvfile)

                # 轉換html至csv格式的dataframe
                df = DataFrameUtils.arrange_html_to_df(rows, date)

                # Save CSV file
                df.to_csv((constants.CSV_FINAL_PATH % date), index=False, header=True)
                df.columns = CollectionUtils.header_daily_stock(constants.HEADERS)

        return df

    @staticmethod
    @interceptor
    def gen_data_direct(date: str) -> DataFrame:
        """ Get data from CSV directly """
        # Empty dataFrame
        df = pandas.DataFrame()
        filepath = (constants.CSV_FINAL_PATH % date)

        if not os.path.isfile(filepath):
            LOG.warning(constants.DATA_NOT_EXIST % date)
        else:
            df = pandas.read_csv(filepath)
            new_headers = CollectionUtils.header_daily_stock(df[:1])
            df.columns = new_headers
            LOG.debug(df)

        return df

    @staticmethod
    @interceptor
    def gen_txt_file(error_dates: list):
        """ Save txt file """
        filepath = constants.URL_ERROR_TXT_PATH % DateUtils.today(constants.YYYY_MM_DD)
        with open(filepath, "w") as output:
            output.write(json.dumps(error_dates))

    @staticmethod
    @interceptor
    def read_txt_file(date: str):
        """ Read txt file """
        filepath = constants.URL_ERROR_TXT_PATH % DateUtils.today(constants.YYYY_MM_DD) if not date else date
        with open(filepath, errors="ignore", encoding="UTF-8") as output:
            content = json.loads(output.read())
            LOG.debug(f"row size: {len(content)}")
            LOG.debug(f"{content}")

        # FIXME return type?
        return content

    @classmethod
    @interceptor
    def fund_html_daily(cls, row) -> DataFrame:
        """ TODO Get HTML from [https://www.moneydj.com/funddj/%s/%s.djhtm?a=%s] """
        LOG.debug(f"fund_html_daily: {row}")
        try:
            url = constants.MONEYDJ_URL % (row.first_url, row.second_url, row.symbol)
            LOG.debug(f"Url: {url}")

            response = urllib.request.urlopen(url, timeout=60)
            soup = BeautifulSoup(response, 'html.parser')
            table = soup.findAll('table')

            if not table:
                LOG.warning(f"Table not exist")
            else:
                # second_url could lead to the different table (for now)
                table_new = table[5] if 'yp010000' == row.second_url else table[4]
                td_tags = table_new.find_all(class_=re.compile("^t3"))
                # log.debug(td_tags)

                data_row = []
                csv_row = []
                for index, cell in enumerate(td_tags):
                    csv_row.append(cell.get_text())
                    """
                    1. csv_row[0] => date (淨值日期)
                    2. csv_row[1] => close price (最新淨值)
                    3. csv_row[2] => ups and downs (每日變化)
                    """
                    if index == 2:
                        csv_row[0] = csv_row[0].replace('/', '')
                        csv_row.insert(1, row.stock_name)
                        csv_row.insert(2, row.symbol)
                        data_row.append(csv_row)
                        csv_row = []
                # log.debug(data_row)

                # FIXME 轉換dataframe
                # df = DataFrameUtils.gen_fund_df(data_row)

                df = pd.DataFrame(data_row)
                df.columns = CollectionUtils.header_fund(HEADERS_DF)
                df = df.astype({CLOSE: float, UPS_AND_DOWNS: float})
                df[UPS_AND_DOWNS] = df[CLOSE] - df[CLOSE].shift(-1, axis=0)
                df.fillna(0, inplace=True)

                return df
        except requests.exceptions.ConnectionError as connError:
            CoreException.show_error(connError, traceback.format_exc())
            time.sleep(10)
            cls.fund_html_range(row)
        except Exception:
            raise
        finally:
            time.sleep(5)

    @classmethod
    @interceptor
    def fund_html_range(cls, row) -> DataFrame:
        """ TODO Get HTML from [https://www.moneydj.com/funddj/%s/%s.djhtm?a=%s] """
        LOG.debug(f"fund_html_range: {row}")
        try:
            url = constants.MONEYDJ_URL % (row.first_url, row.second_url, row.symbol)
            LOG.debug(f"Url: {url}")

            response = urllib.request.urlopen(url, timeout=60)
            soup = BeautifulSoup(response, 'html.parser')
            table = soup.findAll('table')

            if not table:
                LOG.warning(f"Table not exist")
            else:
                # second_url could lead to the different table (for now)
                table_new = table[6] if 'yp010000' == row.second_url else table[5]
                td_tags = table_new.find_all(class_=re.compile("^t3"))

                data_row = []
                csv_row = []
                year = datetime.now().year
                for index, cell in enumerate(td_tags):
                    csv_row.append(cell.get_text())
                    """
                    1. csv_row[0] => date (淨值日期)
                    2. csv_row[1] => close price (最新淨值)
                    """
                    if index % 2 != 0:
                        csv_row[0] = str(year) + csv_row[0].replace('/', '')
                        csv_row.insert(1, row.stock_name)
                        csv_row.insert(2, row.symbol)
                        csv_row.insert(4, 0)
                        data_row.append(csv_row)
                        csv_row = []
                # log.debug(data_row)

                # FIXME 轉換dataframe
                # df = DataFrameUtils.gen_fund_df(data_row)

                df = pd.DataFrame(data_row)
                df.columns = CollectionUtils.header_fund(HEADERS_DF)
                df = df.astype({CLOSE: float, UPS_AND_DOWNS: float})
                df[UPS_AND_DOWNS] = df[CLOSE] - df[CLOSE].shift(-1, axis=0)
                df.fillna(0, inplace=True)

                return df
        except requests.exceptions.ConnectionError as connError:
            CoreException.show_error(connError, traceback.format_exc())
            time.sleep(10)
            cls.fund_html_range(row)
        except Exception:
            raise
        finally:
            time.sleep(5)
