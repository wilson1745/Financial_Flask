import sys
import time
import traceback

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils.constants import YYYYMMDD_SLASH
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.resources import beautifulsoup_stocks, industry_cal, line_notify, potential_stock
from calculations.resources.interfaces.istocks import IStocks

if __name__ == "__main__":
    """
    1. beatifulsoup_stocks: save_db(date, df) -> return dataframe
    2. line_notify: line_notify.sendNotify(stockDict) -> return dict
    3. potential_stock: line_notify.arrangeNotify(potentials, NotifyGroup.getPotentialGroup()) -> return list
    4. industrial_cal: line_notify.sendIndustry(df) -> return dataframe
    """
    now = time.time()
    ms = DateUtils.default_msg(YYYYMMDD_SLASH)

    try:
        line_notify.sendImg('Start.png', 'Start')

        """ 1. beatifulsoup_stocks.py """
        stocks_df = beautifulsoup_stocks.main_daily()
        # Must save today's data
        IStocks.save_db(stocks_df)

        """ 2. line_notify.py """
        stock_dict = line_notify.main_daily()

        """ 3. potential_stock.py """
        potentials_dict = potential_stock.main_daily()

        """ 4. industrial_cal.py """
        industry_df = industry_cal.main_daily()

        # Start the process of Line Notify
        line_notify.sendNotify(stock_dict)
        line_notify.sendNotify(potentials_dict)
        line_notify.sendIndustry(industry_df)

        line_notify.sendImg('Complete.png', 'Complete')
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
