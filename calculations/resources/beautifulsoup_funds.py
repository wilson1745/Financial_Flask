# -*- coding: UTF-8 -*-
import json
import multiprocessing
import os
import socket
import time
import traceback
from datetime import datetime
from multiprocessing.pool import ThreadPool
from urllib.error import URLError
from urllib.request import urlopen

import pandas as pd
import requests
from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.constants import CHANGE, CHANGE_PERCENT, CLOSE, CNYES_URL, DATA_NOT_EXIST, MARKET_DATE, NAV, STOCK_NAME, \
    SUCCESS, SYMBOL, TRADE_DATE, UPS_AND_DOWNS, YYYYMMDD
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_dailyfund import FundGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.common.utils.line_utils import LineUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.dailyfund_repo import DailyFundRepo
from calculations.repository.itemfund_repo import ItemFundRepo
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily
# 設置socket默認的等待時間，在read超時後能自動往下繼續跑
from projects.common.constants import THREAD

socket.setdefaulttimeout(10)


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
        try:
            url = CNYES_URL % (df_row.symbol, current_page)
            LOG.debug(url)
            response = urlopen(url, timeout=120)
            res_data = json.loads(response.read())
            datas = res_data['items']['data']
            # log.debug(datas)

            with parallel_backend(THREAD, n_jobs=-1):
                stream_datas = Parallel()(delayed(cls.__arrange_data)(df_row, data) for data in datas)

            return stream_datas
        except requests.exceptions.ConnectionError as connError:
            LOG.error(f"__get_response ConnectionError: {connError}")
            CoreException.show_error(connError, traceback.format_exc())
            time.sleep(10)
            cls.__get_response(df_row, current_page)
        except URLError as urlError:
            LOG.error(f"__get_response URLError: {urlError}")
            CoreException.show_error(urlError, traceback.format_exc())
            time.sleep(10)
            cls.__get_response(df_row, current_page)
        except Exception:
            raise
        finally:
            time.sleep(6)

    @classmethod
    @interceptor
    def __get_page_data(cls, df_row: tuple, start_page: int, end_page: int):
        """ Crawl page data """
        data_lists = []
        # Range needs plus one
        for current_page in range(start_page, end_page + 1):
            response_list = cls.__get_response(df_row, current_page)
            # Try to drop 'None' in case URLError or other exception return None object
            response_list = list(filter(None, response_list))
            data_lists.extend(response_list)

        df = pd.DataFrame(data_lists)
        df.fillna(0, inplace=True)
        return df

    @classmethod
    def main_old(cls, group: FundGroup):
        """ Grab history data """
        date = DateUtils.today(YYYYMMDD)
        LOG.info(f"start ({DateUtils.today()}): {date}")

        pools = ThreadPool(multiprocessing.cpu_count() - 1)
        try:
            item_df = ItemFundRepo.find_all()
            if item_df.empty:
                LOG.warning(f"itemfund_repo.findAll() is None")
            else:
                """ Daily or Range """
                df_list = pools.map(func=FileUtils.fund_html_daily if group is FundGroup.DAILY else FileUtils.fund_html_range,
                                    iterable=item_df.itertuples())
                df = pd.concat(df_list)

                if not df.empty:
                    # log.debug(df)
                    """ Daily or Range """
                    # print(list(df.itertuples(index=False, name=None)))
                    # print(list(df.itertuples(name=None)))
                    # print(list(df.itertuples(index=False)))
                    # print(df.values.tolist())
                    DailyFundRepo.check_and_save(df.values.tolist())
                else:
                    LOG.warning(DATA_NOT_EXIST)
        except Exception:
            raise
        finally:
            LOG.info(f"end ({DateUtils.today()}): {date}")
            pools.close()

    @classmethod
    @interceptor
    def main_daily(cls, group: FundGroup) -> DataFrame:
        """ 基金DailyFund抓蟲的主程式 """
        date = DateUtils.today(YYYYMMDD)
        LOG.info(f"start ({DateUtils.today()}): {date}")
        lineNotify = LineUtils()

        try:
            start_page = 1
            # Daily or Range
            end_page = 1 if group is FundGroup.DAILY else 6

            item_df = ItemFundRepo.find_first_url_is_null()
            if item_df.empty:
                raise Exception('ItemFundRepo.find_first_url_is_null() is None')
            else:
                df_list = []
                # Use normal loop in case blocking IP
                for item_row in item_df.itertuples(index=False):
                    df = cls.__get_page_data(item_row, start_page, end_page)
                    # Daily or Range
                    df_list.append(df.head(1)) if group is FundGroup.DAILY else df_list.append(df)

                # log.debug(df_list)
                df = pd.concat(df_list)

                if not df.empty:
                    df = df.drop(columns=[TRADE_DATE, NAV, CHANGE, CHANGE_PERCENT])
                    # log.debug(df)

                lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
                return df
        except Exception:
            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            raise
        finally:
            LOG.info(f"end ({DateUtils.today()}): {date}")

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            df = cls.main_daily(FundGroup.DAILY)

            """ Save data """
            if df.empty:
                LOG.warning(f"FileUtils.saveToFinalCsvAndReturnDf({DateUtils.today()}) df is None")
            else:
                DailyFundRepo.check_and_save(df.values.tolist())
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     BeautifulsoupFunds.main()
