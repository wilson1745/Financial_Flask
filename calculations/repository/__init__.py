""" Top level than other modules in core package """
from calculations import log
from calculations.repository.oracle_db import ConnectionPool

pool = ConnectionPool().pool
log.info("Initiallize OracleDB's AdwPool completely")

if __name__ == "__main__":
    log.info("repo 作為主程序啟動")
else:
    log.info("repo 初始化")
