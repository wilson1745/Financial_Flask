import time
import traceback

import mysql.connector
import pyodbc

from calculations import LOG
from calculations.repository import MYSQL_POOL
from projects.common.exceptions.core_exception import CoreException
from projects.common.interceptor import interceptor
from projects.common.utils.db_connections import DbConnections


class IMysqlRepo:
    """ Base Class """

    def __init__(self):
        """ Constructor """
        # 連線池屬性
        # self.pool = ORACLE_POOL
        super().__init__()

    @staticmethod
    @interceptor
    def insert_connector(today, stock_data):
        LOG.info("Save data into MySQL DB")

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
                today,
                row.stock_name, row.symbol, row.deal_stock, row.deal_price, row.open, row.high, row.low, row.close, row.ups_and_downs, row.volume
            )

            cursor = connection.cursor()
            cursor.execute(sql, new_data)

            # 確認資料有存入資料庫
            connection.commit()

            cursor.close()

        connection.close()

    @classmethod
    @interceptor
    def bulk_save(cls, datas: list):
        """ Execute many (fast save) """
        # 顯示目前系統上的所有SQL driver
        # log.debug(pyodbc.drivers())
        LOG.info("Save data into MySQL DB")
        start = time.time()

        # Use the pooled connection
        LOG.debug(f"Current pool: {MYSQL_POOL}")
        connection = MYSQL_POOL.get_connection()
        cursor = connection.cursor()
        try:
            sql = "INSERT INTO financial_db.dailystock (market_date, symbol, stock_name, deal_stock, volume, deal_price, opening_price, " \
                  "highest_price, lowest_price, close_price, ups_and_downs) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            cursor.executemany(sql, datas)
            # 確認資料有存入資料庫
            connection.commit()
        except Exception as e:
            LOG.error(f"bulk_save Exception: {e}")
            connection.rollback()
        finally:
            LOG.debug(f"Time: {time.time() - start}")
            LOG.debug(f"Release connection's cursor: {hex(id(cursor))}")
            cursor.close()

    @staticmethod
    @interceptor
    def save(today, stock_data) -> bool:
        """ Save """
        # 顯示目前系統上的所有SQL driver
        # log.debug(pyodbc.drivers())
        LOG.info("Save data into MySQL DB")

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
                            row.open,
                            row.high,
                            row.low,
                            row.close,
                            row.ups_and_downs,
                            row.volume
                        )
                        conn.commit()

                    return True
                except Exception as e:
                    CoreException.show_error(e, traceback.format_exc())
                    conn.rollback()
