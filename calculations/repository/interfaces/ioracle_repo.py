import time
import traceback

import cx_Oracle

from calculations import LOG
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import ORACLE_POOL


class IOracleRepo:
    """ Base Class """

    def __init__(self):
        """ Constructor """
        # 連線池屬性
        # self.pool = ORACLE_POOL
        pass

    @classmethod
    @interceptor
    def query(cls, sql: str, params=None) -> list:
        """ 查詢方法 """
        # These pool params are suitable for Apache Pre-fork MPM
        LOG.debug(f"Current pool: {ORACLE_POOL}")
        connection = ORACLE_POOL.acquire()
        cursor = connection.cursor()
        try:
            LOG.debug(f"connection: {connection}")
            LOG.debug(f"cursor: {cursor}")
            LOG.debug(f"Sql: {sql}")
            LOG.debug(f"Params: {params}")

            rs = cursor.execute(sql) if not params else cursor.execute(sql, params)
            data = rs.fetchall()
            return data
        except cx_Oracle.Error as e:
            CoreException.show_error(e, traceback.format_exc())
            raise e
        finally:
            LOG.debug(f"Release connection's cursor: {hex(id(cursor))}")
            cursor.close()
            LOG.debug(f"Release pool's connection: {hex(id(connection))}")
            ORACLE_POOL.release(connection)
            # Close the pool
            # pool.close()

    @classmethod
    @interceptor
    def bulk_save(cls, sql: str, datas: list):
        """ Save to Oracle Autonomous DB with bulk insert => fast """
        start = time.time()
        LOG.debug(f"stock_data size:{len(datas)}")

        # Use the pooled connection
        LOG.debug(f"Current pool: {ORACLE_POOL}")
        connection = ORACLE_POOL.acquire()
        cursor = connection.cursor()
        try:
            cursor.executemany(sql, datas)
            connection.commit()
        except cx_Oracle.Error as e:
            LOG.error(f"bulk_save cx_Oracle.Error: {e}")
            """ Rollback to discard them """
            connection.rollback()
            raise e
        finally:
            LOG.debug(f"Time: {time.time() - start}")
            LOG.debug(f"Release connection's cursor: {hex(id(cursor))}")
            cursor.close()

            LOG.debug(f"Release pool's connection: {hex(id(connection))}")
            ORACLE_POOL.release(connection)
            # Close the pool
            # pool.close()

    @interceptor
    def save(self, sql: str, datas: list):
        """ Save to Oracle Autonomous DB by each one => slow """
        start = time.time()
        LOG.debug(f"stock_data size:{len(datas)}")
        LOG.debug(f"Current pool: {ORACLE_POOL}")
        connection = ORACLE_POOL.acquire()

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
                LOG.debug(f"Time: {time.time() - start}")
                LOG.debug(f"Release pool's connection: {hex(id(connection))}")
                ORACLE_POOL.release(connection)
