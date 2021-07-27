# -*- coding: UTF-8 -*-
import os
import sys
import time
import traceback

from pandas import DataFrame

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils.constants import DS_INSERT, TOKEN_NOTIFY, SUCCESS, FAIL, YYYYMMDD_SLASH, YYYYMMDD
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo
from calculations.resources import line_notify


@interceptor
def save_db(df: DataFrame):
    """ Save data into MySQL, Oracle Autonomous """
    log.info(f"start saving db {DateUtils.today()}")

    """ MySQL Database """
    # MySqlUtils.insert_dailystock_mysql(date, df)
    # MySqlUtils.saveDailystockBatch(date, df)

    """ For Mac MySQL connector """
    # MySqlUtils.insert_connector_mysql(date, df)

    """ Oracle Autonomous Database """
    # DailyStockRepo.save(DS_INSERT, df.to_numpy().tolist())

    """ Oracle Autonomous Database (fast batch) """
    DailyStockRepo.bulk_save(DS_INSERT, df.to_numpy().tolist())

    log.info(f"end saving db {DateUtils.today()}")


@interceptor
def main_daily() -> DataFrame:
    """ 台股DailyStock抓蟲的主程式 """
    now = time.time()
    ms = DateUtils.default_msg(YYYYMMDD_SLASH)
    fileName = os.path.basename(__file__)
    date = DateUtils.today(YYYYMMDD)

    # 有資料才使用Line notify
    try:
        log.info(f"start ({DateUtils.today()}): {date}")

        """ Save as HTML file """
        FileUtils.saveToOriginalHtml(date)

        """ Convert to csv file """
        FileUtils.saveToOriginalCsv(date)

        """ Save to db with MI_INDEX_ALLBUT0999 csv file """
        df = FileUtils.saveToFinalCsvAndReturnDf(date)

        log.info(f"end ({DateUtils.today()}): {date}")
        line_notify.sendMsg([ms, SUCCESS % fileName], TOKEN_NOTIFY)
        return df
    except Exception:
        line_notify.sendMsg([ms, FAIL % fileName], TOKEN_NOTIFY)
        raise
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")


@interceptor
def main():
    try:
        df = main_daily()

        """ Save data """
        if df.empty:
            log.warning(f"FileUtils.saveToFinalCsvAndReturnDf({DateUtils.today()}) df is None")
        else:
            save_db(df)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    main()
