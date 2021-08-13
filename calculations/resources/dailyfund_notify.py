# -*- coding: UTF-8 -*-
import os
import traceback
from datetime import datetime

from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame

from calculations.common.constants.constants import FAIL, SUCCESS, THREAD
from calculations.common.enums.enum_line_notify import NotifyGroup
from calculations.common.enums.enum_notifytok import NotifyTok
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.http_utils import HttpUtils
from calculations.common.utils.notify_utils import NotifyUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor
from calculations.repository.dailyfund_repo import DailyFundRepo
from calculations.repository.itemfund_repo import ItemFundRepo
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily


class DailyFundNotify(IFinancialDaily):
    """ 基金通知 """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @staticmethod
    @interceptor
    def query_data(symbol: str) -> DataFrame:
        """ DailyFundRepo """
        LOG.debug(f"Start genNotifyStr: {symbol} at {datetime.now()} ")
        return DailyFundRepo.find_by_symbol(symbol)

    @classmethod
    @interceptor
    def main_daily(cls) -> dict:
        """ 基金通知的主程式 """

        lineNotify = HttpUtils()
        try:
            item_df = ItemFundRepo.find_all()
            symbols = list(item_df.index.values)
            LOG.debug(f"ItemFund Symbols: {symbols}")

            # 產生DailyFund的notify訊息
            with parallel_backend(THREAD, n_jobs=-1):
                df_list = Parallel()(delayed(cls.query_data)(symbol) for symbol in symbols)
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
            NotifyUtils.send_notify(stock_dict, HttpUtils(NotifyTok.FUNDS))
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     DailyFundNotify.main()
