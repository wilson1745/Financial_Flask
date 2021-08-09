# -*- coding: UTF-8 -*-
import os
import time
import traceback
from datetime import datetime

from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.constants import FAIL, RILEY_STOCKS, SUCCESS
from calculations.common.utils.enums.enum_line_notify import NotifyGroup
from calculations.common.utils.enums.enum_notifytok import NotifyTok
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.line_utils import LineUtils
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.core.Interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily
from projects.common.constants import THREAD


class DailyStockNotify(IFinancialDaily):
    """ 台股通知 """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @staticmethod
    @interceptor
    def query_data(symbol: str) -> DataFrame:
        """ DailyStockRepo """
        LOG.debug(f"Start genNotifyStr: {symbol} at {datetime.now()} ")
        return DailyStockRepo.find_by_symbol(symbol)

    @classmethod
    @interceptor
    def main_daily(cls) -> dict:
        """ 通知的主程式 """
        now = time.time()

        lineNotify = LineUtils()
        try:
            symbols = RILEY_STOCKS
            LOG.debug(f"Symbols: {symbols}")

            # 產生DailyStock的notify訊息
            with parallel_backend(THREAD, n_jobs=-1):
                df_list = Parallel()(delayed(cls.query_data)(symbol) for symbol in symbols)
            stocks_dict = NotifyUtils.arrange_notify(df_list, NotifyGroup.getLineGroup())

            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return stocks_dict
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise
        finally:
            LOG.debug(f"Time consuming: {time.time() - now}")

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            # Get data
            stock_dict = cls.main_daily()

            # Send notify
            NotifyUtils.send_notify(stock_dict, LineUtils(NotifyTok.RILEY))
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    DailyStockNotify.main()
