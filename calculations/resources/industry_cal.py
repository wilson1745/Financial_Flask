import os
import sys
import time
import traceback

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.dataframe_utils import DataFrameUtils
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.industry_utils import IndustryUtils
from calculations.resources import line_notify

if __name__ == "__main__":
    """------------------- App Start -------------------"""
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)

    try:
        # IndustryUtils.saveIndustryHtml()
        # IndustryUtils.readHtml()

        industry_rows = IndustryUtils.readPriceIndex()
        df = DataFrameUtils.genIndustryDf(industry_rows)
        line_notify.arrangeIndustry(df)

        line_notify.sendMsg([ms, constants.SUCCESS % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    except Exception as main_e:
        CoreException.show_error(main_e, traceback.format_exc())
        line_notify.sendMsg([ms, constants.FAIL % os.path.basename(__file__)], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
