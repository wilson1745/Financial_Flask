import time
import traceback

import cx_Oracle
import pandas as pd

from calculations import log
from calculations.common.utils.constants import DATA_ALREADY_EXIST
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import pool

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


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
        # log.debug(tuple(params))

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
def findTopOne(market_date: str, symbol: str):
    sql = f"SELECT * FROM DAILYFUND d WHERE d.MARKET_DATE = '{market_date}' AND SYMBOL = '{symbol}' AND rownum = 1 "
    datas = query(sql)
    return datas


@interceptor
def saveToDbBatch(datas: list):
    """ Save to Oracle Autonomous DB with bulk insert => fast """
    start = time.time()
    log.info("Save data into Oracle Autonomous DB")
    log.debug(f"today: {start}, stock_data size:{len(datas)}")

    connection = cx_Oracle.connect(user="admin", password="Wilson155079", dsn="financialdb_medium")
    try:
        sql = "INSERT INTO dailyfund (market_date, stock_name, symbol, close, ups_and_downs) " \
              "values(:market_date, :stock_name, :symbol, :close, :ups_and_downs) "

        cursor = cx_Oracle.Cursor(connection)
        cursor.executemany(sql, datas)

        connection.commit()
        cursor.close()
        connection.close()
    except cx_Oracle.Error as e:
        CoreException.show_error(e, traceback.format_exc())
        """ Rollback to discard them """
        connection.rollback()
    finally:
        log.debug(f"Time: {time.time() - start}")


@interceptor
def saveToDb(datas: list):
    """ Save to Oracle Autonomous DB one by one """
    start = time.time()
    log.info("Save data into Oracle Autonomous DB")
    log.debug(f"today: {start}, stock_data size:{len(datas)}")

    new_list = [row for row in datas if not len(findTopOne(row[0], row[2])) > 0]
    log.debug(new_list)

    if len(new_list) > 0:
        saveToDbBatch(new_list)
    else:
        log.warning('No latest data today!')
