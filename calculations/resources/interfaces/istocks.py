from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import DS_INSERT
from calculations.common.utils.date_utils import DateUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo


class IStocks:
    """ Base Class """

    # def __init__(self):
    #     """ Constructor """

    @classmethod
    @interceptor
    def save_db(cls, df: DataFrame):
        """ Save data into MySQL, Oracle Autonomous """
        log.info(f"start saving db {DateUtils.today()}")

        """ MySQL Database """
        # MySqlUtils.insert_dailystock_mysql(date, df)
        # MySqlUtils.saveDailystockBatch(date, df)

        """ For Mac MySQL connector """
        # MySqlUtils.insert_connector_mysql(date, df)

        """ Oracle Autonomous Database """
        # DailyStockRepo.save(DS_INSERT, df.to_numpy().tolist())

        """ Oracle Autonomous Database (fast batch) """
        DailyStockRepo.bulk_save(DS_INSERT, df.to_numpy().tolist())

        log.info(f"end saving db {DateUtils.today()}")
