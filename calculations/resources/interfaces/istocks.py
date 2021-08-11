from pandas import DataFrame

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
        """ MySQL (fast batch) (備份使用) """
        IMysqlRepo.bulk_save(df.to_numpy().tolist())

        """ Oracle Autonomous (fast batch) """
        DailyStockRepo.bulk_save(sql, df.to_numpy().tolist())
