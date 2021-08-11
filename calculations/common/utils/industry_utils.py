import datetime
import os
import time
import traceback
import urllib
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup

from calculations.common.constants import constants
from calculations.common.exceptions.core_exception import CoreException
from calculations.common.utils.date_utils import DateUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor


class IndustryUtils:
    """ Industry Tools """

    @staticmethod
    @interceptor
    def read_price_index() -> list:
        """ Read HTML """
        isNoFile = True
        date = datetime.datetime.now()
        industry_rows = []

        # Using recursion to read the latest HTML file
        while isNoFile:
            dateStr = DateUtils.datetime_fmt(date, constants.YYYYMMDD)
            filepath = (constants.HTML_PATH % dateStr)

            if not os.path.isfile(filepath):
                LOG.warning(constants.FILE_NOT_EXIST % filepath)
                # 減一天
                date -= datetime.timedelta(days=1)
                continue
            else:
                isNoFile = False
                LOG.debug(f"Reading {filepath}")
                soup = BeautifulSoup(open(filepath, 'r', encoding='UTF-8'), 'html.parser')
                table = soup.findAll('table')

                if not table:
                    LOG.warning(f"Table not exist")
                else:
                    table_last = table[0]
                    rows = table_last.find_all('tr')

                    for index, row in enumerate(rows):
                        rows = []
                        if index > 1:
                            for cell in row.find_all(['td']):
                                rows.append(cell.get_text())
                            # Add a new column (加上日期)
                            rows.append(dateStr)
                            industry_rows.append(rows)

        return industry_rows

    @classmethod
    @interceptor
    def save_industry_html(cls, mode: str = '2') -> None:
        """ Get HTML from [www.twse.com.tw] 本國上市證券國際證券辨識號碼一覽表 """
        LOG.debug(f"readIndustryHtml strMode: {mode}")

        try:
            url = (constants.TWSE_INDUSTRY_INDEX % mode)
            LOG.debug(f"Url: {url}")

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
            LOG.warning(f"ConnectionError: {connError}")
            CoreException.show_error(connError, traceback.format_exc())
            time.sleep(10)
            # again
            cls.save_industry_html()
        except Exception:
            raise

    @staticmethod
    @interceptor
    def read_html():
        """ Read HTML """
        filepath = constants.INDUSTRY_HTML_PATH

        if not os.path.isfile(filepath):
            LOG.warning(constants.FILE_NOT_EXIST % filepath)
        else:
            LOG.debug(f"Reading {filepath}")
            soup = BeautifulSoup(open(filepath, 'r'), 'html.parser')
            table = soup.findAll('table')

            if not table:
                LOG.warning(f"Table not exist")
            else:
                table_last = table[len(table) - 1]
                rows = table_last.find_all('tr')
                LOG.debug(rows[2:10])
