# -*- coding: UTF-8 -*-
import json
import os
import traceback
from datetime import datetime

import pandas as pd
from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame

from calculations.common.constants.constants import CHANGE, CHANGE_PERCENT, CLOSE, CNYES_URL, FAIL, MARKET_DATE, \
    NAV, STOCK_NAME, SUCCESS, SYMBOL, THREAD, TRADE_DATE, UPS_AND_DOWNS, YYYYMMDD
from calculations.common.enums.enum_dailyfund import FundGroup
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.http_utils import HttpUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.dailyfund_repo import DailyFundRepo
from calculations.repository.itemfund_repo import ItemFundRepo
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily


class BeautifulsoupFunds(IFinancialDaily):
    """ BeautifulSoup for funds """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @staticmethod
    @interceptor
    def __arrange_data(df_row, data_row):
        """ Arrange dataframe """
        data_row[TRADE_DATE] = datetime.fromtimestamp(data_row[TRADE_DATE]).strftime(YYYYMMDD)
        data_row[MARKET_DATE] = data_row[TRADE_DATE]
        data_row[STOCK_NAME] = df_row.stock_name
        data_row[SYMBOL] = df_row.symbol
        data_row[CLOSE] = data_row[NAV]
        data_row[UPS_AND_DOWNS] = data_row[CHANGE]
        return data_row

    @classmethod
    def __get_response(cls, df_row: tuple, current_page: int):
        """ Get HTML from [https://fund.api.cnyes.com/fund/api/v1/funds/%s/nav?format=table&page=%s] """
        url = CNYES_URL % (df_row.symbol, current_page)
        response = HttpUtils.url_open(url)
        res_data = json.loads(response.read())
        datas = res_data['items']['data']
        # log.debug(datas)

        with parallel_backend(THREAD, n_jobs=-1):
            stream_datas = Parallel()(delayed(cls.__arrange_data)(df_row, data) for data in datas)

        """ 使用urlopen方法太過頻繁，引起遠程主機的懷疑，被網站認定為是攻擊行為。導致urlopen()後，request.read()一直卡死在那裡。最後拋出10054異常。"""
        response.close()
        return stream_datas

    @classmethod
    @interceptor
    def __get_page_data(cls, df_row: tuple, start_page: int, end_page: int) -> DataFrame:
        """ Crawl page data """
        data_lists = []

        # Range needs plus one
        for current_page in range(start_page, end_page + 1):
            response_list = cls.__get_response(df_row, current_page)
            if response_list is None:
                LOG.warning('No data exist!')
            else:
                # Try to drop 'None' in case URLError or other exception return None object
                LOG.debug(f"response_list: {response_list}")
                response_list = list(filter(None, response_list))
                data_lists.extend(response_list)

        df = pd.DataFrame(data_lists)
        df.fillna(0, inplace=True)
        return df

    @classmethod
    @interceptor
    def main_daily(cls, group: FundGroup, range_list: list = None) -> DataFrame:
        """ 基金DailyFund抓蟲的主程式 """

        lineNotify = HttpUtils()
        try:
            # Daily or Range
            if group is FundGroup.DAILY:
                item_df = ItemFundRepo.find_all()
            else:
                """ 填入新的基金需要傳遞symbols """
                if range_list is None:
                    raise Exception('BeautifulsoupFunds.main_daily: Please fulfill the range_list')
                else:
                    item_df = ItemFundRepo.find_in_symbols(range_list)

            if item_df.empty:
                raise Exception('ItemFundRepo is None')
            else:
                df_list = []

                # # Use normal loop in case blocking IP
                for item_row in item_df.itertuples(index=False):
                    # Daily or Range (start_page = 1, end_page = 1 if group is FundGroup.DAILY else 6)
                    df = cls.__get_page_data(item_row, 1, 1 if group is FundGroup.DAILY else 6)
                    df_list.append(df.head(1)) if group is FundGroup.DAILY else df_list.append(df)
                # log.debug(df_list)

                df = pd.concat(df_list)
                if not df.empty:
                    df.drop(columns=[TRADE_DATE, NAV, CHANGE, CHANGE_PERCENT], inplace=True)

                lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
                return df
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            # df = cls.main_daily(FundGroup.DAILY)
            range_list = ["B20%2C073",
                          "B03%2C013",
                          "B03%2C506",
                          "B03%2C577"]
            df = cls.main_daily(FundGroup.RANGE, range_list)

            """ Save data """
            if df.empty:
                LOG.warning(f"FileUtils {DateUtils.today()}: df is None")
            else:
                DailyFundRepo.check_and_save(df.values.tolist())
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    BeautifulsoupFunds.main()
