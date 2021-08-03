# -*- coding: UTF-8 -*-
from mysql.connector import pooling

from calculations import LOG


class MysqlConnectionPool(object):
    """ MySQL連線池 """

    def __init__(self):
        """ Database Resident Connection Pooling (DRCP) """
        # Create the session pool
        self.pool = pooling.MySQLConnectionPool(pool_name='pynative_pool',
                                                pool_size=5,
                                                pool_reset_session=True,
                                                host='localhost',
                                                database='financial_db',
                                                user='root',
                                                password='1qaz2wsx')
        LOG.debug(f"self.pool: {self.pool}")

# if __name__ == '__main__':
#     pool = MysqlConnectionPool()
#     LOG.debug(pool)
