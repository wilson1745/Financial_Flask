import csv
import multiprocessing
import os
import time
import traceback
from multiprocessing.pool import ThreadPool as Pool

import numpy as np
import pandas as pd

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException

if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    try:
        log.info(f"Test start")
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
        #         results = processPools.map_async(func=DataFrameUtils.test_arrangeMiIndexHtml,
        #                                          iterable=rows[2:],
        #                                          callback=CoreException.show,
        #                                          error_callback=CoreException.error)
        #
        #         if len(results.get()) > 0:
        #             df = pd.DataFrame(results.get())
        #
        #         print(df)
        #
        #         processPools.close()
        #         processPools.join()
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        log.info(f"Test end")
        log.debug(f"Time consuming: {time.time() - now}")
