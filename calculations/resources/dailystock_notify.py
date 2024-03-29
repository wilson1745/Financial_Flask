# -*- coding: UTF-8 -*-
import os
import traceback
from datetime import datetime

from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame

from calculations.common.constants.constants import FAIL, RILEY_STOCKS, SUCCESS, THREAD
from calculations.common.enums.enum_line_notify import NotifyGroup
from calculations.common.enums.enum_notifytok import NotifyTok
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.http_utils import HttpUtils
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.dailystock_repo import DailyStockRepo
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily


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

        lineNotify = HttpUtils()
        try:
            symbols = RILEY_STOCKS
            LOG.debug(f"RILEY_STOCKS: {symbols}")

            # 產生DailyStock的notify訊息
            with parallel_backend(THREAD, n_jobs=-1):
                df_list = Parallel()(delayed(cls.query_data)(symbol) for symbol in symbols)

            """ (Important) Using filter() to remove None values in list """
            df_list = list(filter(lambda df: not df.empty, df_list))
            stocks_dict = NotifyUtils.arrange_notify(df_list, NotifyGroup.getLineGroup())

            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return stocks_dict
        except Exception:
            lineNotify.send_mine(FAIL % os.path.basename(__file__))
            raise

    @classmethod
    @interceptor
    def main(cls):
        """ Main """
        try:
            # Get data
            stock_dict = cls.main_daily()

            # Send notify
            NotifyUtils.send_notify(stock_dict, HttpUtils(NotifyTok.RILEY))
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     DailyStockNotify.main()
