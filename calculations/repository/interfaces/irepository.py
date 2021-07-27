import time
import traceback

import cx_Oracle

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import pool


class IRepository:
    """ Base Class """

    def __init__(self):
        """ Constructor """
        # 連線池屬性
        self.pool = pool

    @classmethod
    @interceptor
    def query(cls, sql: str, params=None) -> list:
        """ 查詢方法 """
        # These pool params are suitable for Apache Pre-fork MPM
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
            log.debug(f"Release connection's cursor: {hex(id(cursor))}")
            cursor.close()
            log.debug(f"Release pool's connection: {hex(id(connection))}")
            pool.release(connection)
            # Close the pool
            # pool.close()

    @classmethod
    @interceptor
    def bulk_save(cls, sql: str, datas: list):
        """ Save to Oracle Autonomous DB with bulk insert => fast """
        start = time.time()
        log.debug(f"stock_data size:{len(datas)}")

        # Use the pooled connection
        log.debug(f"Current pool: {pool}")
        connection = pool.acquire()
        cursor = connection.cursor()
        try:
            cursor.executemany(sql, datas)
            connection.commit()
        except cx_Oracle.Error as e:
            CoreException.show_error(e, traceback.format_exc())
            """ Rollback to discard them """
            connection.rollback()
            raise
        finally:
            log.debug(f"Time: {time.time() - start}")
            log.debug(f"Release connection's cursor: {hex(id(cursor))}")
            cursor.close()

            log.debug(f"Release pool's connection: {hex(id(connection))}")
            pool.release(connection)
            # Close the pool
            # pool.close()

    @interceptor
    def save(self, sql: str, datas: list):
        """ Save to Oracle Autonomous DB by each one => slow """
        start = time.time()
        log.debug(f"stock_data size:{len(datas)}")
        log.debug(f"Current pool: {pool}")
        connection = pool.acquire()

        """ To control the lifetime of a cursor is to use a “with” block, which ensures that a cursor is closed once the block is completed """
        with connection.cursor() as cursor:
            try:
                for row in datas:
                    row.insert(0, DateUtils.today(constants.YYYYMMDD))
                    cursor.execute(sql, row)
                    # Commit to confirm any changes
                    connection.commit()
            except cx_Oracle.Error as e:
                CoreException.show_error(e, traceback.format_exc())
                connection.rollback()
                raise e
            finally:
                log.debug(f"Time: {time.time() - start}")
                log.debug(f"Release pool's connection: {hex(id(connection))}")
                pool.release(connection)
