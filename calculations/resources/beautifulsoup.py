import asyncio
import os
import sys
import time
import traceback
from urllib.error import HTTPError, URLError

import pandas

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.collection_utils import CollectionUtils
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo


@interceptor
async def save_to_final_csv(date):
    # Save CSV and get df
    df = await FileUtils.saveToFinalCsvAndReturnDf(date)

    """ Save data """
    if df.empty:
        log.warning(f"FileUtils.saveToFinalCsvAndReturnDf({date}) df is empty")
    else:
        save_db(date, df)


@interceptor
async def save_data_direct(date):
    filepath = (constants.CSV_FINAL_PATH % date)

    if os.path.isfile(filepath):
        df = pandas.read_csv(filepath)
        new_headers = CollectionUtils.header_daily_stock(df[:1])
        df.columns = new_headers
        save_db(date, df)
    else:
        log.warn(constants.DATA_NOT_EXIST % date)


@interceptor
def save_db(date, df):
    log.info(f"start saving db ({DateUtils.today(constants.YYYYMM_HHMMSS)}): {date}")

    """ For Windows pyodbc MySQL """
    # MySqlUtils.insert_dailystock_mysql(date, df)
    # MySqlUtils.saveDailystockBatch(date, df)

    """ For Mac MySQL connector """
    # MySqlUtils.insert_connector_mysql(date, df.to_numpy().tolist())

    """ Oracle Autonomous Database """
    # OracleSqlUtils.save_data_to_db(date, df)

    """ Oracle with fast batch """
    dailystock_repo.saveToDbBatch(date, df.to_numpy().tolist())

    log.info(f"end saving db ({DateUtils.today(constants.YYYYMM_HHMMSS)}): {date}")


@interceptor
def main():
    try:
        # 時間範圍
        date_list = DateUtils.getDateList(start, ended, "D")
        log.debug(date_list)

        """ Download html file by date """
        for data_date in date_list:
            try:
                log.info(f"Start scraping html ({DateUtils.today(constants.YYYYMM_HHMMSS)}): {data_date}")

                """Save as HTML file"""
                FileUtils.saveToOriginalHtml(data_date)
                # Sleep in case the request is blocked
                time.sleep(6)

                log.info(f"End scraping html ({DateUtils.today(constants.YYYYMM_HHMMSS)}): {data_date}")
            except HTTPError as e_http:
                log.error(f"{os.path.basename(__file__)} HTTPError: ", e_http)
                # TODO Doing something like reactivate the program...
                raise e_http
            except URLError as e_url:
                log.error(f"{os.path.basename(__file__)} URLError: ", e_url)
                # TODO record the error date and still continue the loop
                ERROR_DATES.append(data_date)
                continue

        """
        1. await Separate the loop in case the "urllib.request.urlopen(url)" fail the get the response
        2. async
        """
        """Convert to csv file"""
        tasks1 = [FileUtils.saveToOriginalCsv(data_date) for data_date in date_list]
        asyncio.run(asyncio.wait(tasks1))

        """Save to db with MI_INDEX_ALLBUT0999 csv file"""
        tasks2 = [save_to_final_csv(data_date) for data_date in date_list]
        asyncio.run(asyncio.wait(tasks2))

        """Save to db with STOCK_DAY_ALL csv file"""
        # tasks3 = [save_data_direct(data_date) for data_date in date_list]
        # asyncio.run(asyncio.wait(tasks3))
    except Exception:
        raise


# ------------------- App Start -------------------
if __name__ == "__main__":
    now = time.time()

    start = sys.argv[1] if len(sys.argv) > 1 else "20201207"
    ended = sys.argv[2] if len(sys.argv) > 1 else "20201231"
    index = 0

    ERROR_DATES = []
    try:
        main()
        # FileUtils.readTxtFile(None)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        # Record the error dates
        if len(ERROR_DATES) > 0:
            FileUtils.genTxtFile(ERROR_DATES)

        log.debug(f"Async time consuming: {time.time() - now}")
        log.debug(f"End of {os.path.basename(__file__)}")
