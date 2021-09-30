import datetime
import os

from bs4 import BeautifulSoup

from calculations.common.constants import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.core import LOG
from calculations.core.interceptor import interceptor


class IndustryUtils:
    """ Industry Tools """

    def __init__(self):
        """ Constructor """
        pass

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
