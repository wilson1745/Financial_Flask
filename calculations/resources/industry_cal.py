import os
import traceback

from pandas import DataFrame

from calculations.common.constants.constants import FAIL, RISING_SYMBOLS_PATH, SUCCESS, YYYYMM
from calculations.common.enums.enum_notifytok import NotifyTok
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.file_utils import FileUtils
from calculations.common.utils.http_utils import HttpUtils
from calculations.common.utils.industry_utils import IndustryUtils
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily
from calculations.resources.potential_stock import PotentialStock


class IndustryCalculation(IFinancialDaily):
    """ 台股產業 """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @staticmethod
    @interceptor
    def __write_rising_symbols_txt():
        """ TODO description """
        # 將 lines 所有內容寫入到檔案
        lines = ['1439', '2025', '2029', '2032', '2206', '2428', '2478', '2603', '2614', '2712', '2851', '2881B', '3443', '3661', '3714', '4739',
                 '6213', '6257', '6414', '6451', '6672', '6756', '8482', '910322', '911622', '9937']

        # open file
        with open(RISING_SYMBOLS_PATH, 'w') as fp:
            # write elements of list
            for items in lines:
                fp.write('%s' % items)

        # 關閉檔案
        fp.close()

    @staticmethod
    @interceptor
    def __read_rising_symbols_txt():
        """ TODO description """
        lines = []

        fp = open(RISING_SYMBOLS_PATH, 'r')
        for item in fp.readlines():
            lines.append(item.rstrip('\n'))
        # LOG.debug(len(lines))

        # 關閉檔案
        fp.close()

    @staticmethod
    @interceptor
    def __count_industry(df: DataFrame, potential_list: list) -> list:
        """ 計算產業數，並依數量排序 """
        ind_dict = {}
        for symbol in potential_list:
            r = df.loc[symbol]
            # LOG.debug(r.industry)

            if r.industry not in ind_dict:
                ind_dict[r.industry] = 1
            else:
                ind_dict[r.industry] += 1

        return sorted(ind_dict.items(), key=lambda x: x[1], reverse=True)

    @staticmethod
    @interceptor
    def query_data() -> DataFrame:
        """ 從html抓出有潛力的stock """
        industry_rows = IndustryUtils.read_price_index()
        return DataFrameUtils.gen_industry_df_html(industry_rows)

    @classmethod
    @interceptor
    def main_daily(cls) -> list:
        """ 台股產業現況的主程式(加速度指標所產生的股票代碼) """
        lineNotify = HttpUtils()
        try:
            industry_rows = FileUtils.save_industry_html_return(DateUtils.today(YYYYMM))
            # LOG.debug(f"industry_rows: {industry_rows}")
            industry_df = DataFrameUtils.gen_industry_df(industry_rows)
            # LOG.debug(f"industry_df: {industry_df}")
            potential_list = PotentialStock.get_potentials()
            # LOG.debug(f"potential_list: {potential_list}")

            ind_list = cls.__count_industry(industry_df, potential_list)
            LOG.debug(f"ind_list: {ind_list}")

            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return ind_list
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            industry_df = cls.main_daily()

            """ 送出Line Notify """
            NotifyUtils.send_industry(industry_df, HttpUtils(NotifyTok.RILEY))
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    IndustryCalculation.main()
