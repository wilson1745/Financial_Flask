# -*- coding: UTF-8 -*-
import time
import traceback

import cx_Oracle
import pandas as pd
from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import HEADER_ITEMFUND_E
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import pool


@interceptor
def genDataFrame(datas: list) -> DataFrame:
    """ Generate pandas dataframe """
    try:
        pd.set_option("display.width", None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.unicode.ambiguous_as_wide", True)
        pd.set_option("display.unicode.east_asian_width", True)

        df = pd.DataFrame(datas)
        if df.empty:
            log.warn("No data exist!")
        else:
            df.columns = HEADER_ITEMFUND_E
            df.index = df["symbol"]
            # log.debug(df)

        return df
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        raise e


@interceptor
def query(sql: str, params=None) -> list:
    """ These pool params are suitable for Apache Pre-fork MPM """
    log.debug(f"Current pool: {pool}")
    connection = pool.acquire()

    try:
        # Use the pooled connection
        cursor = connection.cursor()
        log.debug(f"connection.cursor(): {cursor}")
        log.debug(f"Sql: {sql}")
        log.debug(f"Params: {params}")
        rs = cursor.execute(sql) if not params else cursor.execute(sql, params)

        return rs.fetchall()
    except cx_Oracle.Error as e:
        CoreException.show_error(e, traceback.format_exc())
        raise e
    finally:
        # Release the connection to the pool
        log.debug(f"Release pool's connection: {hex(id(connection))}")
        pool.release(connection)
        # Close the pool
        # pool.close()


@interceptor
def findAll() -> DataFrame:
    sql = f"SELECT * FROM ITEMFUND i ORDER BY i.SYMBOL ASC "
    datas = query(sql)
    df = genDataFrame(datas)
    return df


# ------------------- App Start -------------------
if __name__ == "__main__":
    now = time.time()

    try:
        # day = DateUtils.today(Constants.YYYYMMDD)
        result = findAll()
        log.debug(result)
    except Exception as main_e:
        CoreException.show_error(main_e, traceback.format_exc())
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
