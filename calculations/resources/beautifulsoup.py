# -*- coding: UTF-8 -*-
import os
import sys
import time
import traceback

import pandas
import pandas as pd
from joblib import delayed, Parallel, parallel_backend
from pandas import DataFrame

from calculations import LOG
from calculations.common.utils.collection_utils import CollectionUtils
from calculations.common.utils.constants import CSV_FINAL_PATH, DATA_NOT_EXIST, DS_INSERT, FAIL, SUCCESS, THREAD
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.common.utils.line_utils import LineUtils
from calculations.core.Interceptor import interceptor
from calculations.resources.interfaces.istocks import IStocks


class BeautifulSoup(IStocks):
    """ Service BeautifulSoup for range (ex: 20181226 - 20181227) """

    def __init__(self):
        """ Constructor """
        super().__init__()

    @classmethod
    @interceptor
    def __read_data_direct(cls, date) -> DataFrame:
        """ Read data through the csv files and generate dataframe """
        filepath = (CSV_FINAL_PATH % date)
        df = pd.DataFrame()

        if os.path.isfile(filepath):
            df = pandas.read_csv(filepath)
            new_headers = CollectionUtils.header_daily_stock(df[:1])
            df.columns = new_headers
        else:
            LOG.warn(DATA_NOT_EXIST % date)

        return df

    @classmethod
    @interceptor
    def __main_daily(cls, start: str, ended: str) -> DataFrame:
        """ 台股DailyStock抓蟲的主程式 """
        now = time.time()

        lineNotify = LineUtils()
        try:
            date_list = DateUtils.getDateList(start, ended, "D")
            # log.debug(f"Date range: {date_list}")

            """ 1. Download html file by date """
            # for data_date in date_list:
            #     """ Save as HTML file """
            #     FileUtils.save_to_original_html(data_date)

            """ 2. Convert to csv file """
            # # tasks1 = [FileUtils.saveToOriginalCsv(data_date) for data_date in date_list]
            # # asyncio.run(asyncio.wait(tasks1))
            with parallel_backend(THREAD, n_jobs=-1):
                Parallel()(delayed(FileUtils.save_original_csv)(date) for date in date_list)

            """ 3. Convert to MI_INDEX_ALLBUT0999 csv file and return dataframe list """
            # # tasks2 = [save_to_final_csv(data_date) for data_date in date_list]
            # # asyncio.run(asyncio.wait(tasks2))
            with parallel_backend(THREAD, n_jobs=-1):
                df_list = Parallel()(delayed(FileUtils.save_final_csv_return_df)(date) for date in date_list)

            """ 0. Read STOCK_DAY_ALL csv file directly """
            # tasks3 = [save_data_direct(data_date) for data_date in date_list]
            # asyncio.run(asyncio.wait(tasks3))
            # with parallel_backend(THREAD, n_jobs=-1):
            #     df_list = Parallel()(delayed(FileUtils.gen_data_direct)(date) for date in date_list)

            df = pd.concat(df_list)
            # log.debug(df)
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
        """ Main program """
        start = sys.argv[1] if len(sys.argv) > 1 else '20181226'
        ended = sys.argv[2] if len(sys.argv) > 1 else '20190103'

        try:
            df = cls.__main_daily(start, ended)

            """ Save data """
            if df.empty:
                LOG.warning(f"{os.path.basename(__file__)} __main_daily(): df is empty")
            else:
                super().save_db(DS_INSERT, df)
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     BeautifulSoup.main()
#     # FileUtils.readTxtFile(None)
