import sys
import time
import traceback
from multiprocessing.pool import ThreadPool

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import CPU_THREAD, LOG
from calculations.common.utils.constants import COMPLETE, DS_INSERT, START
from calculations.common.utils.enums.enum_notifytok import NotifyTok
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.line_utils import LineUtils
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.resources.beautifulsoup_stocks import BeautifulSoupStocks
from calculations.resources.dailystock_notify import DailyStockNotify
from calculations.resources.industry_cal import IndustryCalculation
from calculations.resources.interfaces.istocks import IStocks
from calculations.resources.potential_stock import PotentialStock

if __name__ == '__main__':
    """
    1. BeautifulSoupStocks.main_daily() -> return dataframe
    2. line_notify: line_notify.sendNotify(stockDict) -> return dict
    3. potential_stock: line_notify.arrangeNotify(potentials, NotifyGroup.getPotentialGroup()) -> return list
    4. industrial_cal: line_notify.sendIndustry(df) -> return dataframe
    """
    now = time.time()

    pools = ThreadPool(CPU_THREAD)
    lineNotify = LineUtils(NotifyTok.RILEY)
    try:
        """ 1. beatifulsoup_stocks.py """
        stocks_df = BeautifulSoupStocks.main_daily()
        # Must save today's data => for line notify
        IStocks.save_db(DS_INSERT, stocks_df)

        """
            map：會等待 map 的任務執行完後，才執行接下來的主程式
            apply_async：不等待 apply_async 的任務執行完，就會執行接下來的主程式
        """
        """ 2. line_utils.py """
        daily_dict = pools.apply_async(DailyStockNotify.main_daily, ())

        """ 3. potential_stock.py """
        potentials_dict = pools.apply_async(PotentialStock.main_daily, ())

        """ 4. industrial_cal.py """
        industry_list = pools.apply_async(IndustryCalculation.main_daily, ())

        # close 和 join 是確保主程序結束後，子程序仍然繼續進行
        pools.close()
        pools.join()

        """ Start the process of Line Notify """
        lineNotify.send_img(START)

        NotifyUtils.send_notify(daily_dict.get(), lineNotify)
        NotifyUtils.send_notify(potentials_dict.get(), lineNotify)
        NotifyUtils.send_industry(industry_list.get(), lineNotify)

        lineNotify.send_img(COMPLETE)

        # daily_dict = DailyStockNotify.main_daily()
        # potentials_dict = PotentialStock.main_daily()
        # industry_df = IndustryCalculation.main_daily()
        # NotifyUtils.send_notify(daily_dict, lineNotify)
        # NotifyUtils.send_notify(potentials_dict, lineNotify)
        # NotifyUtils.send_industry(industry_df, lineNotify)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
    finally:
        LOG.debug(f"Time consuming: {time.time() - now}")
