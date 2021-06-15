import time
import traceback

import mysql.connector
import pyodbc

from calculations import log
from calculations.common.utils.db_connections import DbConnections
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor


@interceptor
def insert_connector_mysql(today, stock_data):
    log.info("Save data into MySQL DB")

    # 連接 MySQL/MariaDB 資料庫
    connection = mysql.connector.connect(
        host='localhost',  # 主機名稱
        database='financial_db',  # 資料庫名稱
        user='root',  # 帳號
        password='1qaz2wsx')  # 密碼

    for index, row in stock_data.iterrows():
        # 新增資料
        sql = 'INSERT INTO financial_db.dailystock (market_date, stock_name, symbol, deal_stock, deal_price, ' \
              'opening_price, highest_price, lowest_price, close_price, ups_and_downs, volume) values(%s,%s,%s,%s,%s,' \
              '%s,%s,%s,%s,%s,%s); '
        new_data = (
            today, row.stock_name, row.symbol, row.deal_stock, row.deal_price, row.opening_price, row.highest_price,
            row.lowest_price, row.close_price, row.ups_and_downs, row.volume)

        cursor = connection.cursor()
        cursor.execute(sql, new_data)

        # 確認資料有存入資料庫
        connection.commit()

        cursor.close()

    connection.close()


@interceptor
def insert_dailystock_mysql(today, stock_data) -> bool:
    # 顯示目前系統上的所有SQL driver
    # log.debug(pyodbc.drivers())
    log.info("Save data into MySQL DB")

    con = DbConnections('mysql')
    with pyodbc.connect(
            f"DRIVER={con.driver};SERVER={con.server};PORT={con.port};DATABASE={con.database};UID={con.username};PWD={con.password}"
    ) as conn:
        with conn.cursor() as cursor:
            try:
                # 把Dataframe 匯入到SQL Server:
                for index, row in stock_data.iterrows():
                    cursor.execute(
                        """INSERT INTO financial_db.dailystock (market_date, stock_name, symbol, deal_stock,
                        deal_price, opening_price, highest_price, lowest_price, close_price, ups_and_downs,
                        volume) values(?,?,?,?,?,?,?,?,?,?,?);""",
                        today,
                        row.stock_name,
                        row.symbol,
                        row.deal_stock,
                        row.deal_price,
                        row.opening_price,
                        row.highest_price,
                        row.lowest_price,
                        row.close_price,
                        row.ups_and_downs,
                        row.volume
                    )

                    # if index % 100 == 0:
                    #     time.sleep(1)

                    conn.commit()

                return True
            except Exception as e:
                CoreException.show_error(e, traceback.format_exc())
                conn.rollback()


@interceptor
def saveDailystockBatch(today: str, stock_data: list):
    # 顯示目前系統上的所有SQL driver
    # log.debug(pyodbc.drivers())
    log.info("Save data into MySQL DB")
    log.debug(f"today: {today}, stock_data size:{len(stock_data)}")
    start = time.time()

    conn = mysql.connector.connect(
        host="localhost",  # 主機名稱
        database="financial_db",  # 資料庫名稱
        user="root",  # 帳號
        password="1qaz2wsx")  # 密碼

    try:
        sql = "INSERT INTO financial_db.dailystock (market_date, symbol, stock_name, deal_stock, volume, deal_price, opening_price, " \
              "highest_price, lowest_price, close_price, ups_and_downs) " \
              "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        cursor = conn.cursor()
        cursor.executemany(sql, stock_data)

        # 確認資料有存入資料庫
        conn.commit()

        if conn.is_connected():
            cursor.close()
            conn.close()
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        conn.rollback()
    finally:
        log.debug(f"Time: {time.time() - start}")
