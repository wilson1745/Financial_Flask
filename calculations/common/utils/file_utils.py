import csv
import json
import os

import pandas
import pandas as pd
import requests
from bs4 import BeautifulSoup
from numpy import iterable
from pandas import DataFrame

from calculations.common.constants import constants
from calculations.common.constants.constants import CSV_PATH, DATA_NOT_EXIST, FILE_NOT_EXIST, HEADERS, HTML_PATH, \
    INDUSTRY_HTML_PATH, INDUSTRY_URL, TWSE_MI_INDEX
from calculations.common.utils.collection_utils import CollectionUtils
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.http_utils import HttpUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


class FileUtils:
    """ 讀取、寫入HTML文件 """

    def __init__(self):
        """ Constructor """
        pass

    @classmethod
    @interceptor
    def __save_html(cls, path: str, url: str):
        """ Get response from url and save it """
        response = HttpUtils.url_open(url)
        webContent = response.read()

        f = open(path, 'wb')
        f.write(webContent)
        f.close()

        """ 使用urlopen方法太過頻繁，引起遠程主機的懷疑，被網站認定為是攻擊行為。導致urlopen()後，request.read()一直卡死在那裡。最後拋出10054異常。"""
        response.close()

    @classmethod
    @interceptor
    def __write_stock_csv(cls, path: str, rows: iterable):
        """ Write data to CSV """
        with open(path, 'w', newline='', encoding='UTF-8') as f:
            writer = csv.writer(f)
            for index, row in enumerate(rows):
                csv_row = []
                for cell in row.find_all(['td']):
                    csv_row.append(cell.get_text())
                # 寫入資料
                writer.writerow(csv_row)

    @classmethod
    @interceptor
    def __write_stock_csv_2(cls, path: str, rows: iterable):
        """ FIXME (Lambda) Write data to CSV """
        with open(path, 'w', newline='', encoding='UTF-8') as f:
            writer = csv.writer(f)
            for index, row in enumerate(rows):
                csv_row = []
                csv_row.extend(list(map(lambda cel: cel.get_text(), row.find_all(['td']))))
                # 寫入資料
                writer.writerow(csv_row)

    @classmethod
    @interceptor
    def __read_stock_csv_to_df(cls, path: str, date: str) -> DataFrame:
        """ Read CSV and generate dataframe """
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
        """
        本國上市證券國際證券辨識號碼一覽表
        Get HTML from [https://isin.twse.com.tw] and return read data
        """
        LOG.debug(f"save_industry_html_return: {date_yyyymm}")

        """ 1. Save html """
        html_path = (INDUSTRY_HTML_PATH % date_yyyymm)
        cls.__save_html(html_path, INDUSTRY_URL)

        """ 2. Scrapy html file (直接在網路上的網頁爬蟲，tr量太多會抓不到。建議下載網頁來爬) """
        # soup = BeautifulSoup(open(html_path, 'r'), from_encoding='UTF-8', features="lxml")
        soup = BeautifulSoup(open(html_path, 'r'), from_encoding='UTF-8', features="html.parser")
        table = soup.findAll('table')
        table_last = table[len(table) - 1]
        rows = table_last.find_all('tr')

        industry_rows = []
        for index, row in enumerate(rows):
            rows = []
            for cell in row.find_all(['td']):
                rows.append(cell.get_text())
            industry_rows.append(rows)

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
        cls.__save_html(html_path, url)

    @classmethod
    @interceptor
    def save_original_csv(cls, date: str):
        """ Save CSV """
        LOG.debug(f"save_original_csv: {date}")
        # Empty dataFrame
        df = pd.DataFrame()

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

    @classmethod
    @interceptor
    def gen_industry_rows(cls) -> list:
        """
        本國上市證券國際證券辨識號碼一覽表
        Get HTML from [https://isin.twse.com.tw] and return read data

        # 有價證券代號及名稱
        # 國際證券辨識號碼(ISIN Code)
        # 上市日
        # 市場別
        # 產業別
        # CFICode
        # 備註
        """

        # 本國上市證券國際證券辨識號碼一覽表
        response = requests.get(INDUSTRY_URL)

        """ 1. Scrapy from html text (直接在網路上的網頁爬蟲) """
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.findAll('table')
        table_last = table[len(table) - 1]
        rows = table_last.find_all('tr')

        industry_rows = []
        for index, row in enumerate(rows):
            rows = []
            for cell in row.find_all(['td']):
                rows.append(cell.get_text())
            industry_rows.append(rows)

        return industry_rows

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
    def write_txt_file(error_dates: list):
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
