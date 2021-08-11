# -*- coding: UTF-8 -*-
"""
https://www.itread01.com/content/1586743325.html
"""
import os
import platform

import cx_Oracle

from calculations import LOG


class OracleConnectionPool(object):
    """ 連線池 """

    def __init__(self):
        """ 2021/04/28 Using path by OS """
        self.system_os = platform.system()
        LOG.debug(f"self.system_os: {self.system_os}")

        if self.system_os == 'Windows':
            """ Using global path variable """
            os.environ.get('TNS_ADMIN')
            LOG.debug(f"os TNS_ADMIN: {os.environ.get('TNS_ADMIN')}")

            """ Using client directly """
            # cx_Oracle.init_oracle_client(lib_dir=Constants.ORACLE_CLIENT_PATH,
            # config_dir=Constants.ORACLE_CLIENT_NETWORK_PATH)
        elif self.system_os == 'Darwin' or self.system_os == 'Linux':
            cx_Oracle.init_oracle_client(lib_dir='/Users/WilsonLo/Downloads/instantclient_19_8',
                                         config_dir='/Users/WilsonLo/oracle/Wallet_financialDB')
        else:
            raise Exception(f"Unknown system: {self.system_os}")

        """ Database Resident Connection Pooling (DRCP) """
        # Create the session pool (user: a?m?? pass: W?????1??0??)
        self.pool = cx_Oracle.SessionPool(user=os.environ.get('ORACLE_ADW_USER'),
                                          password=os.environ.get('ORACLE_ADW_PASS'),
                                          dsn='financialdb_high',
                                          min=1,
                                          max=5,
                                          increment=1,
                                          # Any aquire() call will wait for a connection to become available
                                          getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT,
                                          # Using connections concurrently in multiple threads
                                          threaded=True,
                                          encoding='UTF-8')

        LOG.debug(f"OracleConnectionPool self.pool: {self.pool}")

# if __name__ == '__main__':
#     try:
#         pool = ConnectionPool()
#         log.debug(pool)
#     except Exception as e:
#         CoreException.show(e, traceback.format_exc())
