import datetime
import os
import time
import traceback
import urllib
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor


class IndustryUtils:
    """ Industry Tools """

    @staticmethod
    @interceptor
    def readPriceIndex() -> list:
        """ Read HTML """
        try:
            isNoFile = True
            date = datetime.datetime.now()
            industry_rows = []

            # Using recursion to read the latest HTML file
            while isNoFile:
                dateStr = DateUtils.datetimefmt(date, constants.YYYYMMDD)
                filepath = (constants.HTML_PATH % dateStr)

                if not os.path.isfile(filepath):
                    log.warning(constants.FILE_NOT_EXIST % filepath)
                    # 減一天
                    date -= datetime.timedelta(days=1)
                    continue
                else:
                    isNoFile = False
                    log.debug(f"Reading {filepath}")
                    soup = BeautifulSoup(open(filepath, 'r', encoding='UTF-8'), 'html.parser')
                    table = soup.findAll('table')

                    if not table:
                        log.warning(f"Table not exist")
                    else:
                        table_last = table[0]
                        rows = table_last.findAll('tr')

                        for index, row in enumerate(rows):
                            rows = []
                            if index > 1:
                                for cell in row.findAll(['td']):
                                    rows.append(cell.get_text())
                                # Add a new column (加上日期)
                                rows.append(dateStr)
                                industry_rows.append(rows)

            return industry_rows
        except Exception:
            raise

    @classmethod
    @interceptor
    def saveIndustryHtml(cls, mode: str = '2') -> None:
        """ Get HTML from [www.twse.com.tw] 本國上市證券國際證券辨識號碼一覽表 """
        log.debug(f"readIndustryHtml strMode: {mode}")

        try:
            url = (constants.TWSE_INDUSTRY_INDEX % mode)
            log.debug(f"Url: {url}")

            response = urllib.request.urlopen(url, timeout=60)
            webContent = response.read()

            f = open(constants.INDUSTRY_HTML_PATH, "wb")
            f.write(webContent)
            f.close()

            """ 使用urlopen方法太過頻繁，引起遠程主機的懷疑，被網站認定為是攻擊行為。導致urlopen()後，request.read()一直卡死在那裡。最後拋出10054異常。 """
            response.close()
        except requests.exceptions.ConnectionError as connError:
            # FIXME 觀察一陣子
            """
            如果遇到沒有發送訊息的話，使用[遞歸]重新進行，直到成功為止 (https://www.cnblogs.com/Neeo/articles/11520952.html#urlliberror)
            """
            log.warning(f"ConnectionError: {connError}")
            CoreException.show_error(connError, traceback.format_exc())
            time.sleep(10)
            # again
            cls.saveIndustryHtml()
        except Exception:
            raise

    @staticmethod
    @interceptor
    def readHtml():
        """ Read HTML """
        filepath = constants.INDUSTRY_HTML_PATH

        try:
            if not os.path.isfile(filepath):
                log.warning(constants.FILE_NOT_EXIST % filepath)
            else:
                log.debug(f"Reading {filepath}")
                soup = BeautifulSoup(open(filepath, 'r'), 'html.parser')
                table = soup.findAll('table')

                if not table:
                    log.warning(f"Table not exist")
                else:
                    table_last = table[len(table) - 1]
                    rows = table_last.findAll('tr')
                    log.debug(rows[2:10])
        except Exception:
            raise
