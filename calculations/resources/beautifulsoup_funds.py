# -*- coding: UTF-8 -*-
import json
import multiprocessing
import os
import sys
import time
import traceback
from datetime import datetime
from functools import partial
from multiprocessing.pool import ThreadPool
from urllib.request import urlopen

import pandas as pd
import requests

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils.constants import CLOSE, CNYES_URL, MARKET_DATE, STOCK_NAME, SYMBOL, UPS_AND_DOWNS, TRADE_DATE, NAV, CHANGE, \
    CHANGE_PERCENT, YYYYMMDD, YYYYMMDD_SLASH, SUCCESS, FAIL, TOKEN_NOTIFY, DATA_NOT_EXIST
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_dailyfund import FundGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.dailyfund_repo import DailyFundRepo
from calculations.repository.itemfund_repo import ItemFundRepo
from calculations.resources import line_notify


@interceptor
def main_old(group: FundGroup):
    """ Grab history data """
    date = DateUtils.today(YYYYMMDD)
    log.info(f"start ({DateUtils.today()}): {date}")

    try:
        item_df = ItemFundRepo.find_all()
        if item_df.empty:
            log.warning(f"itemfund_repo.findAll() is None")
        else:
            pools = ThreadPool(multiprocessing.cpu_count() - 1)
            """ Daily or Range """
            df_list = pools.map(func=FileUtils.fundHtmlDaily if group is FundGroup.DAILY else FileUtils.fundHtmlRange,
                                iterable=item_df.itertuples())
            df = pd.concat(df_list)

            if not df.empty:
                # log.debug(df)
                """ Daily or Range """
                # print(list(df.itertuples(index=False, name=None)))
                # print(list(df.itertuples(name=None)))
                # print(list(df.itertuples(index=False)))
                # print(df.values.tolist())

                # DailyFundRepo.check_and_save(list(df.itertuples())) if group is FundGroup.DAILY \
                #     else DailyFundRepo.check_and_save(df.values.tolist())
                DailyFundRepo.check_and_save(df.values.tolist())
            else:
                log.warning(DATA_NOT_EXIST)
    except Exception:
        raise
    finally:
        log.info(f"end ({DateUtils.today()}): {date}")


@interceptor
def arrangeData(df_row, data_row):
    """ Arrange dataframe """
    data_row[TRADE_DATE] = datetime.fromtimestamp(data_row[TRADE_DATE]).strftime(YYYYMMDD)
    data_row[MARKET_DATE] = data_row[TRADE_DATE]
    data_row[STOCK_NAME] = df_row.stock_name
    data_row[SYMBOL] = df_row.symbol
    data_row[CLOSE] = data_row[NAV]
    data_row[UPS_AND_DOWNS] = data_row[CHANGE]
    return data_row


def getResponse(df_row: tuple, current_page: int) -> list:
    """ Get HTML from [https://fund.api.cnyes.com/fund/api/v1/funds/%s/nav?format=table&page=%s] """
    try:
        url = CNYES_URL % (df_row.symbol, current_page)
        log.debug(url)
        response = urlopen(url, timeout=120)
        res_data = json.loads(response.read())
        datas = res_data['items']['data']
        # log.debug(datas)

        pools = ThreadPool(multiprocessing.cpu_count() - 1)
        partial_func = partial(arrangeData, df_row)
        stream_datas = pools.map(func=partial_func,
                                 iterable=datas)

        return stream_datas
    except requests.exceptions.ConnectionError as connError:
        CoreException.show_error(connError, traceback.format_exc())
        time.sleep(15)
        getResponse(df_row, current_page)
    except Exception:
        raise
    finally:
        time.sleep(6)


@interceptor
def getPageData(df_row: tuple, start_page: int, end_page: int):
    """ Crawl page data """
    data_lists = []
    # Range needs plus one
    for current_page in range(start_page, end_page + 1):
        data_lists.extend(getResponse(df_row, current_page))

    df = pd.DataFrame(data_lists)
    df.fillna(0, inplace=True)
    return df


@interceptor
def main(group: FundGroup):
    """ Grab history data """
    date = DateUtils.today(YYYYMMDD)
    log.info(f"start ({DateUtils.today()}): {date}")

    try:
        start_page = 1
        # Daily or Range
        end_page = 1 if group is FundGroup.DAILY else 6

        item_df = ItemFundRepo.find_first_url_is_null()
        if item_df.empty:
            log.warning('ItemFundRepo.find_first_url_is_null() is None')
        else:
            df_list = []
            for item_row in item_df.itertuples(index=False):
                df = getPageData(item_row, start_page, end_page)
                # Daily or Range
                df_list.append(df.head(1)) if group is FundGroup.DAILY else df_list.append(df)

            # log.debug(df_list)
            df = pd.concat(df_list)

            if not df.empty:
                df = df.drop(columns=[TRADE_DATE, NAV, CHANGE, CHANGE_PERCENT])
                log.debug(df)
                DailyFundRepo.check_and_save(df.values.tolist())
            else:
                log.warning(DATA_NOT_EXIST)
    except Exception:
        raise
    finally:
        log.info(f"end ({DateUtils.today()}): {date}")


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(YYYYMMDD_SLASH)
    fileName = os.path.basename(__file__)

    try:
        main(FundGroup.DAILY)
        # main(FundGroup.RANGE)
        line_notify.sendMsg([ms, SUCCESS % fileName], TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        line_notify.sendMsg([ms, FAIL % fileName], TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")
