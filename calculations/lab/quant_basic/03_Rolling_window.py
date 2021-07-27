import os
import time
import traceback

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.constants import MARKET_DATE
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
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

        log.debug(MA_5.head(10))
        log.debug(MA_5)
        log.debug(MA_20)
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
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")
