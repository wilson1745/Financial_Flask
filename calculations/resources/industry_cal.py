import os
import time
import traceback

from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.constants import FAIL, RISING_SYMBOLS_PATH, SUCCESS
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.enums.enum_industry import IndustryGroup
from calculations.common.utils.enums.enum_notifytok import NotifyTok
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.industry_utils import IndustryUtils
from calculations.common.utils.line_utils import LineUtils
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.core.Interceptor import interceptor
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily


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

        print(len(lines))

        # 關閉檔案
        fp.close()

    @staticmethod
    @interceptor
    def __define_industry():
        """ TODO description """
        # a = [(item.value, item.name) for item in IndustryGroup]
        # stockDict: dict = {}
        # for item in IndustryGroup:
        #     stockDict[item] = []
        # print(stockDict)  # prints [1, 2]
        # print(IndustryGroup.__values__())
        print(IndustryGroup["18"])

        # enum_list = list(map(IndustryGroup, IndustryGroup))
        # print(enum_list)  # prints [1, 2]

    @staticmethod
    @interceptor
    def query_data() -> DataFrame:
        """ 抓出有潛力的stock """
        industry_rows = IndustryUtils.readPriceIndex()
        return DataFrameUtils.gen_industry_df(industry_rows)

    @classmethod
    @interceptor
    def main_daily(cls) -> DataFrame:
        """ 台股產業現況的主程式 """
        now = time.time()

        lineNotify = LineUtils()
        try:
            # IndustryUtils.saveIndustryHtml()
            # IndustryUtils.readHtml()

            # writeRisingSymbolsTxt()
            # readRisingSymbolsTxt()
            # defineIndustry()

            df = cls.query_data()

            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return df
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise
        finally:
            LOG.debug(f"Time consuming: {time.time() - now}")

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            industry_df = cls.main_daily()

            """ 送出Line Notify """
            NotifyUtils.send_industry(industry_df, LineUtils(NotifyTok.RILEY))
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     IndustryCalculation.main()
