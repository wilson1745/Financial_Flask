import time
import traceback

import cx_Oracle
import pandas as pd
from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import HEADERS_T
from calculations.common.utils.enums.enum_yes_no import YesNo
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import pool


@interceptor
def genDataFrame(datas: list) -> DataFrame:
    """ Generate pandas dataframe """
    try:
        pd.set_option("display.width", 320)
        pd.set_option("display.max_columns", 20)
        pd.set_option("display.max_rows", None)
        pd.set_option("display.unicode.ambiguous_as_wide", True)
        pd.set_option("display.unicode.east_asian_width", True)

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
def saveToDbBatch(today: str, stock_data: list):
    """ Save to Oracle Autonomous DB with bulk insert => fast """
    start = time.time()
    log.info("Save data into Oracle Autonomous DB")
    log.debug(f"today: {today}, stock_data size:{len(stock_data)}")

    connection = cx_Oracle.connect(user="admin", password="Wilson155079", dsn="financialdb_medium")
    try:
        sql = "INSERT INTO dailystock (market_date, symbol, stock_name, deal_stock, volume, deal_price, opening_price, highest_price, " \
              "lowest_price, close_price, ups_and_downs) values(:market_date, :symbol, :stock_name, :deal_stock, :volume, :deal_price, " \
              ":opening_price, :highest_price, :lowest_price, :close_price, :ups_and_downs) "
        cursor = cx_Oracle.Cursor(connection)
        cursor.executemany(sql, stock_data)

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
def saveToBb(today, stock_data):
    """ Save to Oracle Autonomous DB by each one => slow """
    start = time.time()
    log.info("Save data into Oracle Autonomous DB")
    log.debug(f"today: {today}, stock_data size:{len(stock_data)}")

    connection = cx_Oracle.connect(user="admin", password="Wilson155079", dsn="financialdb_medium")

    """ To control the lifetime of a cursor is to use a “with” block, which ensures that a cursor is closed once the block is completed """
    with connection.cursor() as cursor:
        log.debug(f"connection.cursor(): {cursor}")
        try:
            for index, row in stock_data.iterrows():
                sql = (
                    "INSERT INTO dailystock (market_date, stock_name, symbol, deal_stock, deal_price, opening_price, highest_price, lowest_price, "
                    "close_price, ups_and_downs, volume) values(:market_date, :stock_name, :symbol, :deal_stock, :deal_price, :opening_price, "
                    ":highest_price, :lowest_price, :close_price, :ups_and_downs, :volume) ")

                new_data = (today,
                            row.stock_name,
                            row.symbol,
                            row.deal_stock,
                            row.deal_price,
                            row.opening_price,
                            row.highest_price,
                            row.lowest_price,
                            row.close_price,
                            row.ups_and_downs,
                            row.volume)

                cursor = connection.cursor()
                cursor.execute(sql, new_data)

                # Commit to confirm any changes
                connection.commit()

                if index % 100 == 0:
                    time.sleep(1)

        except cx_Oracle.Error as e:
            CoreException.show_error(e, traceback.format_exc())
            """ Rollback to discard them """
            connection.rollback()
        finally:
            log.debug(f"Time: {time.time() - start}")


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


# ------------------- App Start -------------------
if __name__ == "__main__":
    now = time.time()

    try:
        # day = DateUtils.today(Constants.YYYYMMDD)
        day = '20210513'
        result = checkExistByMarketDate(day)
        log.debug(f"checkExistByMarketDate(date): {result}")

    except Exception as main_e:
        CoreException.show_error(main_e, traceback.format_exc())
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
