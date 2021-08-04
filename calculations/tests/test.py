import time
import traceback

from calculations import LOG
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException


def test_ex():
    stdd = "ddd"
    raise Exception("...........")


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    try:
        data_lists = []
        data_lists.extend(["A", "B", "C"])
        lisss = [None, None]
        lisss = list(filter(None, lisss))
        print(lisss)
        data_lists.extend(lisss)
        print(data_lists)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        LOG.info(f"Test end")
        LOG.debug(f"Time consuming: {time.time() - now}")
