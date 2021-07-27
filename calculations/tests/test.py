import time
import traceback

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_test import Fingers
from calculations.common.utils.exceptions.core_exception import CoreException


def test_ex():
    try:
        stdd = "ddd"
        raise Exception("...........")
    except Exception as ex:
        CoreException.show_error(ex, traceback.format_exc())


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    try:
        test_ex()

        # print(Fingers.THUMB.__str__())
        # print(Fingers('1'))

        # log.info(f"Test start")
        #
        # lines = ['1439', '2025', '2029', '2032', '2206', '2428', '2478', '2603', '2614', '2712', '2851', '2881B', '3443', '3661', '3714', '4739',
        #          '6213', '6257', '6414', '6451', '6672', '6756', '8482', '910322', '911622', '9937']
        #
        # ig = IndustryGroup.getAllInMaps()
        #
        # # for l in lines:
        #
        # print(IndustryGroup("綜合"))
        # print(ig)

        # df = dailystock_repo.findAllSymbolGroup()
        #
        # line_notify.arrangeNotify(df[SYMBOL].values.tolist(), NotifyGroup.getLineGroup())

        # filepath = (constants.CSV_PATH % "20210701")
        #
        # # Empty dataFrame
        # df = pd.DataFrame()
        #
        # if not os.path.isfile(filepath):
        #     log.warning(constants.FILE_NOT_EXIST % filepath)
        # else:
        #     log.debug(f"Reading {filepath}")
        #     with open(filepath, errors="ignore", encoding="UTF-8") as csvfile:
        #         # 讀取 CSV 檔案內容
        #         rows = list(csv.reader(csvfile))
        #
        #         df = pd.DataFrame()
        #         processPools = Pool(multiprocessing.cpu_count() - 1)
        #         results = processPools.map(func=DataFrameUtils.test_arrangeMiIndexHtml, iterable=rows[2:])
        #
        #         if len(results.get()) > 0:
        #             df = pd.DataFrame(results.get())
        #
        #         print(df)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        log.info(f"Test end")
        log.debug(f"Time consuming: {time.time() - now}")
