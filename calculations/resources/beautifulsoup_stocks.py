# -*- coding: UTF-8 -*-
import os
import time
import traceback

from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.constants import DS_INSERT, FAIL, SUCCESS, YYYYMMDD
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.common.utils.line_utils import LineUtils
from calculations.core.Interceptor import interceptor
from calculations.resources.interfaces.ifinancial_daily import IFinancialDaily
from calculations.resources.interfaces.istocks import IStocks


class BeautifulSoupStocks(IStocks, IFinancialDaily):
    """ BeautifulSoup for range (ex: 20181226 - 20181227) """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @classmethod
    @interceptor
    def main_daily(cls) -> DataFrame:
        """ 台股DailyStock抓蟲的主程式 """
        now = time.time()
        date = DateUtils.today(YYYYMMDD)

        lineNotify = LineUtils()
        # 有資料才使用Line notify
        try:
            """ Save as HTML file """
            FileUtils.save_to_original_html(date)

            """ Convert to csv file """
            FileUtils.save_to_original_csv(date)

            """ Save to db with MI_INDEX_ALLBUT0999 csv file """
            df = FileUtils.save_to_final_csv_return_df(date)

            lineNotify.send_mine(SUCCESS % os.path.basename(__file__))
            return df
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
            df = cls.main_daily()

            """ Save data """
            if df.empty:
                LOG.warning(f"FileUtils.saveToFinalCsvAndReturnDf({DateUtils.today()}) df is None")
            else:
                super().save_db(DS_INSERT, df)
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())

# if __name__ == "__main__":
#     """ ------------------- App Start ------------------- """
#     BeautifulSoupStocks.main()
