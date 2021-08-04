# -*- coding: UTF-8 -*-
import time
import traceback

import pandas as pd
from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository.interfaces.ioracle_repo import IOracleRepo

pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)


class ItemFundRepo(IOracleRepo):
    """ Table ITEMFUND """

    @classmethod
    @interceptor
    def find_all(cls) -> DataFrame:
        """ find_all """
        sql = f"SELECT * FROM ITEMFUND i ORDER BY i.SYMBOL ASC "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_item_df(datas)

    @classmethod
    @interceptor
    def find_first_url_is_null(cls) -> DataFrame:
        """ find_first_url_is_null """
        sql = f"SELECT * FROM ITEMFUND i WHERE i.FIRST_URL IS NULL ORDER BY i.SYMBOL ASC  "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_item_df(datas)


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    now = time.time()
    try:
        result = ItemFundRepo.find_all()
        # log.debug(result)
        # log.debug(list(result.index.values))
    except Exception as main_e:
        CoreException.show_error(main_e, traceback.format_exc())
    finally:
        LOG.debug(f"Time consuming: {time.time() - now}")
