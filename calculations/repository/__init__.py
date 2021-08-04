""" Top level than other modules in core package """
from calculations import LOG
from calculations.repository.mysql_db import MysqlConnectionPool
from calculations.repository.oracle_db import OracleConnectionPool

MYSQL_POOL = MysqlConnectionPool().pool
LOG.info("Initiallize MySQL's database completely")

ORACLE_POOL = OracleConnectionPool().pool
LOG.info("Initiallize OracleDB's AdwPool completely")

if __name__ == '__main__':
    LOG.info("Repository 作為主程序啟動")
else:
    LOG.info("Repository 初始化")
