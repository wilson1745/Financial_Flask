import os
import sys
import time
import traceback

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.constants import RISING_SYMBOLS_PATH
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_industry import IndustryGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.industry_utils import IndustryUtils
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


if __name__ == "__main__":
    """------------------- App Start -------------------"""
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
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
        line_notify.sendIndustry(df)

        line_notify.sendMsg([ms, constants.SUCCESS % fileName], constants.TOKEN_NOTIFY)
    except Exception as main_e:
        CoreException.show_error(main_e, traceback.format_exc())
        line_notify.sendMsg([ms, constants.FAIL % fileName], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
