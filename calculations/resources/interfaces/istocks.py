from pandas import DataFrame

from calculations import log
from calculations.common.utils.date_utils import DateUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.interfaces.irepository import IRepository


class IStocks:
    """ Service Base Class """

    def __init__(self):
        """ Constructor """
        pass

    @classmethod
    @interceptor
    def save_db(cls, sql: str, df: DataFrame):
        """ Save data into MySQL, Oracle Autonomous """
        log.info(f"start saving db {DateUtils.today()}")

        """ MySQL Database """
        # MySqlUtils.insert_dailystock_mysql(date, df)
        # MySqlUtils.saveDailystockBatch(date, df)

        """ For Mac MySQL connector """
        # MySqlUtils.insert_connector_mysql(date, df)

        """ Oracle Autonomous Database """
        # IRepository.save(sql, df.to_numpy().tolist())

        """ Oracle Autonomous Database (fast batch) """
        IRepository.bulk_save(sql, df.to_numpy().tolist())

        log.info(f"end saving db {DateUtils.today()}")
