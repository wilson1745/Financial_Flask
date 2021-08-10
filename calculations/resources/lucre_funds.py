import os
import sys
import time
import traceback

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import LOG
from calculations.common.utils.constants import COMPLETE, START
from calculations.common.utils.enums.enum_dailyfund import FundGroup
from calculations.common.utils.enums.enum_notifytok import NotifyTok
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.repository.dailyfund_repo import DailyFundRepo
from calculations.resources.beautifulsoup_funds import BeautifulsoupFunds
from calculations.resources.dailyfund_notify import DailyFundNotify
from calculations.common.utils.line_utils import LineUtils

if __name__ == '__main__':
    """
    1. BeautifulsoupFunds.main_daily(FundGroup.DAILY) -> return dataframe
    2. DailyFundNotify.main_daily() -> return dict
    """
    now = time.time()

    lineNotify = LineUtils(NotifyTok.FUNDS)
    try:
        lineNotify.send_mine(START % os.path.basename(__file__))

        """ 1. beatifulsoup_funds.py """
        df_fund = BeautifulsoupFunds.main_daily(FundGroup.DAILY)
        # Must save today's data
        if df_fund.empty:
            LOG.warning(f"BeautifulsoupFunds.main_daily: df is None")
        else:
            DailyFundRepo.check_and_save(df_fund.values.tolist())

        """ 2. dailyfund_notify.py """
        fund_dict = DailyFundNotify.main_daily()

        """ Start the process of Line Notify """
        lineNotify.send_img(START)
        NotifyUtils.send_notify(fund_dict, lineNotify)
        lineNotify.send_img(COMPLETE)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        # TODO send fail image
    finally:
        LOG.debug(f"Time consuming: {time.time() - now}")
