# -*- coding: UTF-8 -*-
import asyncio
import multiprocessing
import os
import sys
import time
import traceback
import urllib
from multiprocessing.pool import ThreadPool as Pool
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_moneydj import MoneyDj
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import itemfund_repo
from calculations.resources import line_notify


@interceptor
def readHtml(symbol: str, func: MoneyDj = MoneyDj.NET_WORTH):
    try:
        # html_path = (constants.HTML_PATH % date)
        url = constants.MONEYDJ_URL % (func.getCaption(), symbol)
        log.debug(f"Url: {url}")

        # response = urllib.request.urlopen(url, timeout=60)
        # webContent = response.read()
        # # log.debug(webContent)
        #
        # soup = BeautifulSoup(open(webContent, 'r', encoding="UTF-8"), 'html.parser')
        # table = soup.findAll('table')
        # print(table)

        response = urllib.request.urlopen(url, timeout=60)
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.findAll('table')
        # print(table)

        if not table:
            log.warning(f"Table not exist")
        else:
            table_new = table[5]
            print(table_new)

        """ 使用urlopen方法太過頻繁，引起遠程主機的懷疑，被網站認定為是攻擊行為。導致urlopen()後，request.read()一直卡死在那裡。最後拋出10054異常。 """
        response.close()
    except requests.exceptions.ConnectionError as connError:
        CoreException.show_error(connError, traceback.format_exc())
        time.sleep(10)
        readHtml()
    except Exception:
        raise
    finally:
        time.sleep(5)


@interceptor
async def main():
    # Multiprocessing 設定處理程序數量
    # processPools = Pool(4)
    processPools = Pool(multiprocessing.cpu_count() - 1)

    try:
        date = DateUtils.today(constants.YYYYMMDD)
        log.info(f"start ({DateUtils.today()}): {date}")

        item_df = itemfund_repo.findAll()
        if item_df.empty:
            log.warning(f"itemfund_repo.findAll() is None")
        else:
            results = processPools.map_async(func=readHtml,
                                             iterable=item_df.index,
                                             callback=CoreException.show,
                                             error_callback=CoreException.error)

        # readHtml(MoneyDj.NET_WORTH, 'ACYT152')

        log.info(f"end ({DateUtils.today()}): {date}")
    except Exception:
        raise
    finally:
        # 關閉process的pool並等待所有process結束
        processPools.close()
        processPools.join()


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    fileName = os.path.basename(__file__)

    # 有資料才使用Line notify
    try:
        asyncio.run(main())

        line_notify.sendMsg([ms, constants.SUCCESS % fileName], constants.TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        line_notify.sendMsg([ms, constants.FAIL % fileName], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")
