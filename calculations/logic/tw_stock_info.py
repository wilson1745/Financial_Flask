# -*- coding: UTF-8 -*-
import datetime
import re

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from calculations.common.constants.constants import INDUSTRY_URL
from calculations.core import LOG
from calculations.core.interceptor import interceptor

pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)


class TwStockInfo:
    """
    資料來源：本國上市證券國際證券辨識號碼一覽表
    https://isin.twse.com.tw/isin/C_public.jsp?strMode=2
    """

    def __init__(self):
        """ Constructor """
        pass

    @classmethod
    @interceptor
    def __ymd(cls, series):
        """ 處理爬蟲完的資料 (Industry) """

        """ 轉換數字轉換成日期格式，如20210614變成2021-06-14 """
        if isinstance(series, str):
            explode = False

            if '-' in series:
                series = series.split('-')
                explode = True

            if '/' in series:
                series = series.split('/')
                explode = True

            if explode:
                series = ["{:02d}".format(int(i)) for i in series]
                series = series[0] + series[1] + series[2]

            series = int(series)

            # or np.int64 == np.dtype(type(series)).type \\
        if isinstance(series, int) or isinstance(series, np.int32) or isinstance(series, np.int64) or isinstance(series, str):
            series = str(series)
            series = datetime.datetime(year=int(series[0:4]),
                                       month=int(series[4:6]),
                                       day=int(series[6:8]))

        return series

    @classmethod
    @interceptor
    def get_tw_stock_info(cls):
        """
        # 有價證券代號及名稱
        # 國際證券辨識號碼(ISIN Code)
        # 上市日
        # 市場別
        # 產業別
        # CFICode
        # 備註
        """

        r = requests.get(INDUSTRY_URL)
        soup = BeautifulSoup(r.text, 'html.parser')

        # Parse update date
        update_date = soup.select('.h1 center')[0]
        update_date = update_date.text
        update_date = re.search('(\\d+/\\d+/\\d+)', update_date)
        update_date = update_date.group(1)
        LOG.debug('get_stock_info資料源更新時間為' + update_date)

        # Parse table ......
        table = soup.select('table.h4')[0]
        rows = table.find_all('tr')

        stock_list_raw = []
        for i in range(0, len(rows)):
            cells = rows[i].find_all('td')
            single_stock = []

            for j in range(0, len(cells)):
                single_stock.append(cells[j].text)

            stock_list_raw.append(single_stock)

        stock_list_pre = pd.DataFrame(stock_list_raw)

        # 有價證券代號及名稱 STOCK_SYMBOL
        # 國際證券辨識號碼(ISIN Code) ISIN_CODE
        # 上市日 LISTING_DATE
        # 市場別 MARKET
        # 產業別 INDUSTRY
        # CFICode CFI_CODE
        # 備註 NOTE
        cols = ['STOCK_SYMBOL_RAW', 'ISIN_CODE', 'LISTING_DATE', 'MARKET', 'INDUSTRY', 'CFI_CODE', 'NOTE']
        stock_list_pre.columns = cols
        stock_list_pre = stock_list_pre.iloc[1:, :]
        stock_list_pre = stock_list_pre[~stock_list_pre['CFI_CODE'].isna()]
        stock_list_pre['ID'] = stock_list_pre.index

        # 將股票代號和名稱拆開 ......
        stock_symbol = stock_list_pre['STOCK_SYMBOL_RAW'].str.split('　', expand=True)
        stock_symbol.columns = ['STOCK_SYMBOL', 'STOCK_NAME']
        stock_symbol['ID'] = stock_symbol.index

        # 整理資料 ......
        stock_info = stock_list_pre.merge(stock_symbol, on='ID')
        stock_info['LISTING_DATE'].apply(cls.__ymd)
        stock_info = stock_info[['STOCK_SYMBOL', 'STOCK_NAME', 'ISIN_CODE', 'LISTING_DATE', 'MARKET', 'INDUSTRY', 'CFI_CODE']]

        return stock_info


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    data = TwStockInfo.get_tw_stock_info()
    LOG.debug(f"{data}")
