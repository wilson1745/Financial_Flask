import time
import traceback

import cx_Oracle
import pandas as pd

from calculations import log
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import pool
from projects.common.constants import DATA_NOT_EXIST

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


@interceptor
def query(sql: str, params=None) -> list:
    """ These pool params are suitable for Apache Pre-fork MPM """
    # Use the pooled connection
    log.debug(f"Current pool: {pool}")
    connection = pool.acquire()
    cursor = connection.cursor()

    try:
        log.debug(f"connection: {connection}")
        log.debug(f"cursor: {cursor}")
        log.debug(f"Sql: {sql}")
        log.debug(f"Params: {params}")

        rs = cursor.execute(sql) if not params else cursor.execute(sql, params)
        data = rs.fetchall()

        return data
    except cx_Oracle.Error as e:
        CoreException.show_error(e, traceback.format_exc())
        raise e
    finally:
        # Release the cursor of the connection
        log.debug(f"Release connection's cursor: {hex(id(cursor))}")
        cursor.close()
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
    log.debug(f"today: {start}, stock_data size:{len(datas)}")

    # Use the pooled connection
    log.debug(f"Current pool: {pool}")
    connection = pool.acquire()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO dailyfund (market_date, stock_name, symbol, close, ups_and_downs) " \
              "values(:market_date, :stock_name, :symbol, :close, :ups_and_downs) "

        cursor.executemany(sql, datas)
        connection.commit()
    except cx_Oracle.Error as e:
        CoreException.show_error(e, traceback.format_exc())
        """ Rollback to discard them """
        connection.rollback()
    finally:
        log.debug(f"Time: {time.time() - start}")
        # Release the cursor of the connection
        log.debug(f"Release connection's cursor: {hex(id(cursor))}")
        cursor.close()
        # Release the connection to the pool
        log.debug(f"Release pool's connection: {hex(id(connection))}")
        pool.release(connection)
        # Close the pool
        # pool.close()


@interceptor
def checkAndSave(data_map: map):
    """ Check DB data one by one """
    new_datas = [row for row in data_map if not len(findTopOne(row.market_date, row.symbol)) > 0]
    # log.debug(new_datas)

    if len(new_datas) > 0:
        saveToDbBatch(new_datas)
    else:
        log.warning(DATA_NOT_EXIST)
