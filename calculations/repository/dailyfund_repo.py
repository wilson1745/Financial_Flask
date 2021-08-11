from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame

from calculations.common.constants.constants import DF_INSERT, THREAD
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.interfaces.ioracle_repo import IOracleRepo
from projects.common.constants import DATA_NOT_EXIST


class DailyFundRepo(IOracleRepo):
    """ Table DAILYFUND """

    @classmethod
    @interceptor
    def __check_exist(cls, row):
        """ Filter data if exist """
        return row if not len(cls.find_top_by_marketdate_symbol(row[0], row[2])) > 0 else None

    @classmethod
    @interceptor
    def find_by_symbol(cls, symbol: str) -> DataFrame:
        """ find_by_symbol """
        sql = f"SELECT * FROM DAILYFUND d WHERE d.SYMBOL = '{symbol}' ORDER BY d.MARKET_DATE ASC "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_fund_df(datas)

    @classmethod
    @interceptor
    def find_top_by_marketdate_symbol(cls, market_date: str, symbol: str) -> list:
        """ find_top_by_marketdate_symbol """
        sql = f"SELECT * FROM DAILYFUND d WHERE d.MARKET_DATE = '{market_date}' AND SYMBOL = '{symbol}' AND rownum = 1 "
        return super().query(sql=sql)

    @classmethod
    @interceptor
    def check_and_save(cls, rows: list):
        """ Check DB data one by one """
        with parallel_backend(THREAD, n_jobs=-1):
            new_rows = Parallel()(delayed(cls.__check_exist)(row) for row in rows)

        if len(new_rows) > 0:
            LOG.debug(f"check_and_save: {new_rows}")
            super().bulk_save(DF_INSERT, list(filter(None, new_rows)))
        else:
            LOG.warning(DATA_NOT_EXIST)


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    df = DailyFundRepo.find_by_symbol('B03%2C631')
    LOG.debug(df)
