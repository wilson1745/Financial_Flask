import json
import multiprocessing
import time
import traceback
from datetime import datetime
from functools import partial
from multiprocessing.pool import ThreadPool
from urllib.request import urlopen

import pandas as pd
import requests

from calculations import LOG
from calculations.common.utils import constants
from calculations.common.utils.constants import CLOSE, CNYES_URL, MARKET_DATE, STOCK_NAME, SYMBOL, UPS_AND_DOWNS
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_dailyfund import FundGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository.dailyfund_repo import DailyFundRepo
from calculations.repository.itemfund_repo import ItemFundRepo

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


@interceptor
def arrangeData(df_row, data_row):
    data_row['tradeDate'] = datetime.fromtimestamp(data_row['tradeDate']).strftime('%Y%m%d')
    data_row[MARKET_DATE] = data_row['tradeDate']
    data_row[STOCK_NAME] = df_row.stock_name
    data_row[SYMBOL] = df_row.symbol
    data_row[CLOSE] = data_row['nav']
    data_row[UPS_AND_DOWNS] = data_row['change']
    return data_row


def __getResponse(df_row: tuple, current_page: int) -> list:
    """ TODO Description """
    try:
        url = CNYES_URL % (df_row.symbol, current_page)
        LOG.debug(url)
        response = urlopen(url)
        res_data = json.loads(response.read())
        datas = res_data['items']['data']
        # log.debug(datas)

        pools = ThreadPool(multiprocessing.cpu_count() - 1)
        func = partial(arrangeData, df_row)
        stream_datas = pools.map(func=func,
                                 iterable=datas)

        return stream_datas
    except requests.exceptions.ConnectionError as connError:
        CoreException.show_error(connError, traceback.format_exc())
        time.sleep(15)
        __getResponse(df_row, current_page)
    except Exception:
        raise
    finally:
        time.sleep(6)


@interceptor
def getPageData(df_row: tuple, start_page: int, end_page: int):
    """ TODO Get HTML from [https://www.moneydj.com/funddj/%s/%s.djhtm?a=%s] """
    data_lists = []
    # Range needs plus one
    for current_page in range(start_page, end_page + 1):
        data_lists.extend(__getResponse(df_row, current_page))

    df = pd.DataFrame(data_lists)
    df.fillna(0, inplace=True)
    return df


@interceptor
def main(group: FundGroup):
    """ Grab history data """
    date = DateUtils.today(constants.YYYYMMDD)
    LOG.info(f"start ({DateUtils.today()}): {date}")

    try:
        start_page = 1
        end_page = 6

        item_df = ItemFundRepo.find_first_url_is_null()
        if item_df.empty:
            LOG.warning('ItemFundRepo.find_first_url_is_null() is None')
        else:
            df_list = []
            for item_row in item_df.itertuples(index=False):
                df = getPageData(item_row, start_page, end_page)
                df_list.append(df)

            df = pd.concat(df_list)

            if not df.empty:
                df.drop(columns=['tradeDate', 'nav', 'change', 'changePercent'], inplace=True)
                LOG.debug(df)
                DailyFundRepo.check_and_save(df.values.tolist())
            else:
                LOG.warning(constants.DATA_NOT_EXIST)
    except Exception:
        raise
    finally:
        LOG.info(f"end ({DateUtils.today()}): {date}")


@interceptor
def main_daily():
    """ Grab history data """
    date = DateUtils.today(constants.YYYYMMDD)
    LOG.info(f"start ({DateUtils.today()}): {date}")

    try:
        start_page = 1
        end_page = 1

        item_df = ItemFundRepo.find_first_url_is_null()
        if item_df.empty:
            LOG.warning('ItemFundRepo.find_first_url_is_null() is None')
        else:
            df_list = []
            for item_row in item_df.itertuples(index=False):
                df = getPageData(item_row, start_page, end_page)
                df_list.append(df.head(1))

            # log.debug(df_list)
            df = pd.concat(df_list)

            if not df.empty:
                df.drop(columns=['tradeDate', 'nav', 'change', 'changePercent'], inplace=True)
                LOG.debug(df)
                # DailyFundRepo.check_and_save(df.values.tolist())
            else:
                LOG.warning(constants.DATA_NOT_EXIST)
    except Exception:
        raise
    finally:
        LOG.info(f"end ({DateUtils.today()}): {date}")


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """

    # main(FundGroup.RANGE)
    main_daily()
