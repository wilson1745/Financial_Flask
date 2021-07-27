import os
import sys
import time
import traceback

from pandas import DataFrame

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils.constants import FAIL, RISING_SYMBOLS_PATH, SUCCESS, TOKEN_NOTIFY, YYYYMMDD_SLASH
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_industry import IndustryGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.industry_utils import IndustryUtils
from calculations.core.Interceptor import interceptor
from calculations.resources import line_notify


def writeRisingSymbolsTxt():
    # 將 lines 所有內容寫入到檔案
    lines = ['1439', '2025', '2029', '2032', '2206', '2428', '2478', '2603', '2614', '2712', '2851', '2881B', '3443', '3661', '3714', '4739', '6213',
             '6257', '6414', '6451', '6672', '6756', '8482', '910322', '911622', '9937']

    # open file
    with open(RISING_SYMBOLS_PATH, 'w') as fp:
        # write elements of list
        for items in lines:
            fp.write('%s' % items)

    # 關閉檔案
    fp.close()


def readRisingSymbolsTxt():
    lines = []

    fp = open(RISING_SYMBOLS_PATH, 'r')

    for item in fp.readlines():
        lines.append(item.rstrip('\n'))

    print(len(lines))

    # 關閉檔案
    fp.close()


def defineIndustry():
    # a = [(item.value, item.name) for item in IndustryGroup]
    # stockDict: dict = {}
    # for item in IndustryGroup:
    #     stockDict[item] = []
    # print(stockDict)  # prints [1, 2]
    # print(IndustryGroup.__values__())
    print(IndustryGroup["18"])

    # enum_list = list(map(IndustryGroup, IndustryGroup))
    # print(enum_list)  # prints [1, 2]


@interceptor
def main_daily() -> DataFrame:
    """ 台股產業現況的主程式 """
    now = time.time()
    ms = DateUtils.default_msg(YYYYMMDD_SLASH)
    fileName = os.path.basename(__file__)

    try:
        # IndustryUtils.saveIndustryHtml()
        # IndustryUtils.readHtml()

        # writeRisingSymbolsTxt()
        # readRisingSymbolsTxt()
        # defineIndustry()

        """ 抓出有潛力的stock """
        industry_rows = IndustryUtils.readPriceIndex()
        df = DataFrameUtils.genIndustryDf(industry_rows)

        line_notify.sendMsg([ms, SUCCESS % fileName], TOKEN_NOTIFY)
        return df
    except Exception:
        line_notify.sendMsg([ms, FAIL % fileName], TOKEN_NOTIFY)
        raise
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")


@interceptor
def main():
    try:
        df = main_daily()

        """ 送出Line Notify """
        line_notify.sendIndustry(df)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    main()
