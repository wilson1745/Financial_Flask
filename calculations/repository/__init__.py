# -*- coding: UTF-8 -*-
from calculations.common.constants.constants import INIT
from calculations.core import LOG
from calculations.repository.driver.mysql_db import MysqlConnectionPool
from calculations.repository.driver.oracle_db import OracleConnectionPool

""" Initialize driver for MySQL """
MYSQL_POOL = MysqlConnectionPool().pool

""" Initialize driver for Oracle """
ORACLE_POOL = OracleConnectionPool().pool

if __name__ == '__main__':
    LOG.info(f"Calculations Repository {INIT} 作為主程序啟動")
else:
    LOG.info(f"Calculations Repository {INIT} 初始化")
