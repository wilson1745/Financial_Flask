# -*- coding: UTF-8 -*-
import asyncio
import os
import sys
import time
import traceback

from pandas import DataFrame

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo
from calculations.resources import line_notify


@interceptor
def save_db(date: str, df: DataFrame):
    log.info(f"start saving db ({DateUtils.today()}): {date}")

    """ For Windows pyodbc MySQL """
    # MySqlUtils.insert_dailystock_mysql(date, df)
    # MySqlUtils.saveDailystockBatch(date, df)

    """ For Mac MySQL connector """
    # MySqlUtils.insert_connector_mysql(date, df)

    """ Oracle Autonomous Database """
    # OracleSqlUtils.save_data_to_db(date, df)

    """ Oracle with fast batch """
    dailystock_repo.saveToDbBatch(date, df.to_numpy().tolist())

    log.info(f"end saving db ({DateUtils.today()}): {date}")


@interceptor
async def main():
    date = DateUtils.today(constants.YYYYMMDD)
    log.info(f"start ({DateUtils.today()}): {date}")

    """ Save as HTML file """
    FileUtils.saveToOriginalHtml(date)

    """ Convert to csv file """
    await asyncio.create_task(FileUtils.saveToOriginalCsv(date))

    """ Save to db with MI_INDEX_ALLBUT0999 csv file """
    df = await asyncio.create_task(FileUtils.saveToFinalCsvAndReturnDf(date))

    """ Save data """
    if df.empty:
        log.warning(f"FileUtils.saveToFinalCsvAndReturnDf({date}) df is None")
    else:
        save_db(date, df)

    log.info(f"end ({DateUtils.today()}): {date}")


# ------------------- App Start -------------------
if __name__ == "__main__":
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)

    # 有資料才使用Line notify
    try:
        asyncio.run(main())

        line_notify.sendMsg([ms, constants.SUCCESS % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        line_notify.sendMsg([ms, constants.FAIL % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {os.path.basename(__file__)}")
