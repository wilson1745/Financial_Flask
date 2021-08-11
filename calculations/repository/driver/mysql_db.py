# -*- coding: UTF-8 -*-
from mysql.connector import pooling

from calculations.core import LOG
from calculations.core.interceptor import interceptor


class MysqlConnectionPool(object):
    """ MySQL連線池 """

    @interceptor
    def __init__(self):
        """ Database Resident Connection Pooling (DRCP) """
        LOG.info("Initialize MySQL's database")
        # Create the session pool
        self.pool = pooling.MySQLConnectionPool(pool_name='pynative_pool',
                                                pool_size=5,
                                                pool_reset_session=True,
                                                host='localhost',
                                                database='financial_db',
                                                user='root',
                                                password='1qaz2wsx')

        LOG.debug(f"MysqlConnectionPool self.pool: {self.pool}")

# if __name__ == '__main__':
#     pool = MysqlConnectionPool()
#     LOG.debug(pool)
