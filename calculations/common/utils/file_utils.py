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
from numpy import iterable
from pandas import DataFrame

from calculations.common.constants import constants
from calculations.common.constants.constants import CLOSE, CSV_PATH, DATA_NOT_EXIST, FILE_NOT_EXIST, HEADERS, HEADERS_DF, HTML_PATH, \
    INDUSTRY_HTML_PATH, INDUSTRY_URL, TWSE_MI_INDEX, UPS_AND_DOWNS
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.collection_utils import CollectionUtils
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
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
    """ 讀取、寫入HTML文件 """

    @classmethod
    @interceptor
    def __save_html(cls, html_path: str, url: str):
        """ Get response from url and save it """
        try:
            response = urlopen(url, timeout=600)
            webContent = response.read()

            f = open(html_path, 'wb')
            f.write(webContent)
            f.close()

            """ 使用urlopen方法太過頻繁，引起遠程主機的懷疑，被網站認定為是攻擊行為。導致urlopen()後，request.read()一直卡死在那裡。最後拋出10054異常。 """
            response.close()
        except (requests.exceptions.ConnectionError, URLError) as error:
            CoreException.show_error(error, traceback.format_exc())
            time.sleep(10)
            # (FIXME 觀察一陣子)使用[遞歸]重新進行，直到成功為止
            cls.__save_html(html_path, url)
        except Exception:
            raise
        finally:
            # Sleep in case the request is blocked
            time.sleep(6)

    @classmethod
    @interceptor
    def __write_stock_csv(cls, path: str, rows: iterable):
        """ TODO description """
        with open(path, 'w', newline='', encoding='UTF-8') as f:
            writer = csv.writer(f)
            for index, row in enumerate(rows):
                csv_row = []
                for cell in row.find_all(['td']):
                    csv_row.append(cell.get_text())
                # 寫入資料
                writer.writerow(csv_row)

                # if not index == 1:
                #     for cell in row.find_all(['td']):
                #         csv_row.append(cell.get_text())
                #     writer.writerow(csv_row)

    @classmethod
    @interceptor
    def __read_stock_csv_to_df(cls, path: str, date: str) -> DataFrame:
        """ TODO description """
        with open(path, errors='ignore', encoding='UTF-8') as csvfile:
            # 讀取 CSV 檔案內容
            read_rows = csv.reader(csvfile)
            # 轉換html至csv格式的dataframe
            df = DataFrameUtils.arrange_html_to_df(read_rows, date)
            # # (暫時不需要再儲存) Save CSV file
            # df.to_csv((constants.CSV_FINAL_PATH % date), index=False, header=True)
            # 產生headers
            df.columns = CollectionUtils.header_daily_stock(HEADERS)
        return df

    @classmethod
    @interceptor
    def save_industry_html_return(cls, date_yyyymm: str) -> list:
        """ Get HTML from [https://isin.twse.com.tw] and return read data """
        LOG.debug(f"save_industry_html: {date_yyyymm}")

        """ 1. Save html """
        html_path = (INDUSTRY_HTML_PATH % date_yyyymm)
        url = INDUSTRY_URL
        LOG.debug(f"Url: {url}")
        cls.__save_html(html_path, url)

        """ 2. Scrapy html file (直接在網路上爬蟲，tr量太多會抓不到) """
        soup = BeautifulSoup(open(html_path, 'r'), from_encoding='UTF-8', features="lxml")
        table = soup.findAll('table')
        table_last = table[len(table) - 1]
        rows = table_last.find_all('tr')

        industry_rows = []
        for index, row in enumerate(rows):
            rows = []
            for cell in row.find_all(['td']):
                rows.append(cell.get_text())
            industry_rows.append(rows)

            # LOG.debug(industry_rows)
        return industry_rows

    @classmethod
    @interceptor
    def save_original_html(cls, date: str):
        """ Get HTML from [www.twse.com.tw] """
        # log.debug(f"{inspect.currentframe().f_code.co_name}: {date}")
        LOG.debug(f"save_original_html: {date}")

        """ 不管如何都儲存成html檔 => 證交所2pm才會有當天資料 """
        # ex: url = f"https://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date={date}&type=ALLBUT0999"
        html_path = (HTML_PATH % date)
        url = (TWSE_MI_INDEX % ("html", date, "ALLBUT0999"))
        LOG.debug(f"Url: {url}")

        cls.__save_html(html_path, url)

    @classmethod
    @interceptor
    def save_original_csv(cls, date: str):
        """ Save CSV """
        LOG.debug(f"{inspect.currentframe().f_code.co_filename}.{inspect.currentframe().f_code.co_name}: {date}")
        LOG.debug(f"save_original_csv: {date}")

        filepath = (HTML_PATH % date)
        if not os.path.isfile(filepath):
            LOG.warning(FILE_NOT_EXIST % filepath)
        else:
            LOG.debug(f"Reading {filepath}")
            # Start scrapy the html file
            soup = BeautifulSoup(open(filepath, 'r', encoding='UTF-8'), 'html.parser')
            tables = soup.findAll('table')

            if not tables:
                LOG.warning(DATA_NOT_EXIST % date)
            else:
                table_last = tables[len(tables) - 1]
                rows = table_last.find_all('tr')
                # 去除非相關的headers
                rows = rows[2:]

                csv_filepath = (CSV_PATH % date)
                cls.__write_stock_csv(csv_filepath, rows)
                df = cls.__read_stock_csv_to_df(csv_filepath, date)

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
    def fund_html_daily_moneydj(cls, row) -> DataFrame:
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
