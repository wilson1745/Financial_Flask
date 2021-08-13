# -*- coding: UTF-8 -*-
import pandas as pd
from pandas import DataFrame

from calculations.common.constants.constants import SYMBOL
from calculations.common.enums.enum_yes_no import YesNo
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.interfaces.ioracle_repo import IOracleRepo

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)


class DailyStockRepo(IOracleRepo):
    """ Table DAILYSTOCK """

    @classmethod
    @interceptor
    def find_by_symbol(cls, symbol: str) -> DataFrame:
        """ find_by_symbol """
        sql = f"SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL = '{symbol}' ORDER BY d.MARKET_DATE ASC "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_stock_df(datas)

    @classmethod
    @interceptor
    def find_in_symbols(cls, params: list) -> DataFrame:
        """ find_in_symbols """
        bindNames = [":" + str(i + 1) for i in range(len(params))]
        sql = "SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL IN (%s) ORDER BY d.MARKET_DATE ASC " % (",".join(bindNames))
        datas = super().query(sql=sql, params=params)
        return DataFrameUtils.gen_stock_df(datas)

    @classmethod
    @interceptor
    def find_month_by_symbol_and_yearmonth(cls, symbol: str, year_month: str) -> DataFrame:
        """ find_month_by_symbol_and_yearmonth """
        sql = f"SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL = '{symbol}' AND d.MARKET_DATE LIKE '{year_month}%' ORDER BY " \
              f"d.MARKET_DATE ASC "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_stock_df(datas)

    @classmethod
    @interceptor
    def find_by_symbol_and_market_with_range(cls, symbol: str, start: str, end: str) -> DataFrame:
        """ find_by_symbol_and_market_with_range """
        sql = f"SELECT * FROM DAILYSTOCK d WHERE d.SYMBOL = '{symbol}' AND d.MARKET_DATE >= '{start}' AND d.MARKET_DATE <= '{end}' ORDER BY " \
              f"d.MARKET_DATE ASC "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_stock_df(datas)

    @classmethod
    @interceptor
    def check_exist_by_marketdate(cls, date: str) -> bool:
        """ Check exist by market_date """
        sql = f"SELECT CASE WHEN EXISTS (SELECT 1 FROM DAILYSTOCK d WHERE d.MARKET_DATE = {date}) " \
              f"THEN '{YesNo.Y.name}' ELSE '{YesNo.N.name}' END AS rec_exists FROM dual "
        results = super().query(sql=sql)
        return True if YesNo.Y.name in results[0] else False

    @classmethod
    @interceptor
    def find_like_year(cls, param: str) -> DataFrame:
        """ find_like_year """
        sql = f"SELECT * FROM DAILYSTOCK d WHERE d.MARKET_DATE LIKE '{param}%' ORDER BY d.MARKET_DATE ASC "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_stock_df(datas)

    @classmethod
    @interceptor
    def find_all_symbol_group(cls) -> DataFrame:
        """ Find all symbols """
        sql = 'SELECT d.SYMBOL FROM DAILYSTOCK d GROUP BY d.SYMBOL ORDER BY d.SYMBOL ASC '
        datas = super().query(sql=sql)
        df = pd.DataFrame(datas)

        if df.empty:
            LOG.warn('No data exist!')
        else:
            df.columns = [SYMBOL]
            df.index = df[SYMBOL]

        return df
