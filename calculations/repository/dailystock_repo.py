# -*- coding: UTF-8 -*-
import time
import traceback

import cx_Oracle
import pandas as pd
from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import HEADERS_T, SYMBOL
from calculations.common.utils.enums.enum_yes_no import YesNo
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
def genDataFrame(datas: list) -> DataFrame:
    """ Generate pandas dataframe """
    try:
        df = pd.DataFrame(datas)
        if df.empty:
            log.warn("No data exist!")
        else:
            df.columns = HEADERS_T
            df.index = pd.to_datetime(df["market_date"])
            # log.debug(df)
        return df
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        raise e


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
def saveToDbBatch(today: str, stock_data: list):
    """ Save to Oracle Autonomous DB with bulk insert => fast """
    start = time.time()
    log.debug(f"today: {today}, stock_data size:{len(stock_data)}")

    # Use the pooled connection
    log.debug(f"Current pool: {pool}")
    connection = pool.acquire()
    cursor = connection.cursor()
    try:
        sql = "INSERT INTO dailystock (market_date, symbol, stock_name, deal_stock, volume, deal_price, open, high, low, close, ups_and_downs) " \
              "values(:market_date, :symbol, :stock_name, :deal_stock, :volume, :deal_price, :open, :high, :low, :close, :ups_and_downs) "

        cursor.executemany(sql, stock_data)
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
def findBySymbol(symbol: str) -> DataFrame:
    sql = f"SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL = '{symbol}' ORDER BY d.MARKET_DATE ASC "
    datas = query(sql)
    df = genDataFrame(datas)
    return df


@interceptor
def findInSymbols(params: list) -> DataFrame:
    bindNames = [":" + str(i + 1) for i in range(len(params))]
    sql = "SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL IN (%s) ORDER BY d.MARKET_DATE ASC " % (",".join(bindNames))
    datas = query(sql, params)
    df = genDataFrame(datas)
    return df


@interceptor
def findMonthBySymbolAndYearMonth(symbol: str, year_month: str) -> DataFrame:
    sql = f"SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL = '{symbol}' AND d.MARKET_DATE LIKE '{year_month}%' ORDER BY " \
          f"d.MARKET_DATE ASC "
    datas = query(sql)
    df = genDataFrame(datas)
    return df


@interceptor
def findBySymbolAndMarketWithRange(symbol: str, start: str, end: str) -> DataFrame:
    sql = f"SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL = '{symbol}' AND d.MARKET_DATE >= '{start}' AND d.MARKET_DATE <= '{end}' ORDER BY " \
          f"d.MARKET_DATE ASC "
    datas = query(sql)
    df = genDataFrame(datas)
    return df


@interceptor
def checkExistByMarketDate(date: str) -> bool:
    """ Check exist by market_date """
    sql = f"SELECT CASE WHEN EXISTS (SELECT 1 FROM DAILYSTOCK d WHERE d.MARKET_DATE = {date}) " \
          f"THEN '{YesNo.Y.name}' ELSE '{YesNo.N.name}' END AS rec_exists FROM dual "
    results = query(sql)
    return True if YesNo.Y.name in results[0] else False


@interceptor
def findLikeYear(param: str):
    """ FIXME """
    sql = f"SELECT * FROM DAILYSTOCK d WHERE d.MARKET_DATE LIKE '{param}%' ORDER BY d.MARKET_DATE ASC "
    datas = query(sql)
    results = genDataFrame(datas)
    return results


@interceptor
def findAllSymbolGroup() -> DataFrame:
    sql = 'SELECT d.SYMBOL FROM DAILYSTOCK d GROUP BY d.SYMBOL ORDER BY d.SYMBOL ASC '
    datas = query(sql)
    df = pd.DataFrame(datas)

    if df.empty:
        log.warn('No data exist!')
    else:
        df.columns = [SYMBOL]
        df.index = df[SYMBOL]

    return df


# ------------------- App Start -------------------
if __name__ == '__main__':
    now = time.time()

    try:
        # day = DateUtils.today(Constants.YYYYMMDD)
        # day = '20210513'
        # result = checkExistByMarketDate(day)

        result = findAllSymbolGroup()

        log.debug(f"dailystock_repo: {result}")
    except Exception as main_e:
        CoreException.show_error(main_e, traceback.format_exc())
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
