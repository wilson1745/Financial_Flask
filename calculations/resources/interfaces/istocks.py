from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.date_utils import DateUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo
from calculations.repository.interfaces.imysql_repo import IMysqlRepo


class IStocks:
    """ Service Base Class """

    def __init__(self):
        """ Constructor """
        pass

    @classmethod
    @interceptor
    def save_db(cls, sql: str, df: DataFrame):
        """ Save data into MySQL, Oracle Autonomous """
        today = DateUtils.today()
        LOG.info(f"Start saving db {today}")

        """ MySQL (fast batch) (備份使用) """
        IMysqlRepo.bulk_save(df.to_numpy().tolist())

        """ For Mac MySQL connector """
        # MySqlUtils.insert_connector_mysql(date, df)

        """ Oracle Autonomous (fast batch) """
        DailyStockRepo.bulk_save(sql, df.to_numpy().tolist())

        LOG.info(f"End saving db {today}")
