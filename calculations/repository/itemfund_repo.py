# -*- coding: UTF-8 -*-

import pandas as pd
from pandas import DataFrame

from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.core.interceptor import interceptor
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
    def find_all_act(cls) -> DataFrame:
        """ find_all """
        sql = f"SELECT * FROM ITEMFUND i WHERE i.ACT_FLG = 'Y' ORDER BY i.SYMBOL ASC "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_item_df(datas)

    @classmethod
    @interceptor
    def find_first_url_is_null(cls) -> DataFrame:
        """ find_first_url_is_null """
        sql = f"SELECT * FROM ITEMFUND i WHERE i.FIRST_URL IS NULL ORDER BY i.SYMBOL ASC  "
        datas = super().query(sql=sql)
        return DataFrameUtils.gen_item_df(datas)

    @classmethod
    @interceptor
    def find_in_symbols(cls, params: list) -> DataFrame:
        """ find_in_symbols """
        bindNames = [":" + str(i + 1) for i in range(len(params))]
        sql = "SELECT * FROM ITEMFUND d WHERE d.SYMBOL IN (%s) ORDER BY d.SYMBOL ASC " % (",".join(bindNames))
        datas = super().query(sql=sql, params=params)
        return DataFrameUtils.gen_item_df(datas)

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     try:
#         lists = ["B3ja88k",
#                  "B09%2C007",
#                  "B16%2C019",
#                  "B09%2C005",
#                  "A2Ml9IZ"]
#
#         result = ItemFundRepo.find_all_act()
#         # result = ItemFundRepo.find_in_symbols(lists)
#         LOG.debug(result)
#         # log.debug(list(result.index.values))
#     except Exception as main_e:
#         CoreException.show_error(main_e, traceback.format_exc())
