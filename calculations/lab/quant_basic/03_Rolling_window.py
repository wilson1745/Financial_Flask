import os
import time
import traceback

from calculations.common.constants import constants
from calculations.common.constants.constants import MARKET_DATE
from calculations.common.utils.date_utils import DateUtils
from calculations.common.exceptions.core_exception import CoreException
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo


@interceptor
def main():
    try:
        symbol = "2330"
        data = DailyStockRepo.find_by_symbol(symbol)
        data.drop(MARKET_DATE, axis=1, inplace=True)
        # log.debug(data.head())

        df = data.copy()
        MA_5 = df.rolling(5).mean()
        MA_20 = df.rolling(20).mean()
        MA_5.dropna(inplace=True)

        LOG.debug(MA_5.head(10))
        LOG.debug(MA_5)
        LOG.debug(MA_20)
    except Exception:
        raise


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    fileName = os.path.basename(__file__)

    # 有資料才使用Line notify
    try:
        main()
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        LOG.debug(f"Time consuming: {time.time() - now}")
        LOG.debug(f"End of {fileName}")
