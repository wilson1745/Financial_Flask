import logging
from datetime import datetime

import pandas

from projects.common.constants import LOG_PROJECTS, YYYYMMDD
from projects.common.interceptor import interceptor

log = logging.getLogger(LOG_PROJECTS)


class DateUtils:

    @staticmethod
    @interceptor
    def getDateList(date_start: str, date_end: str, frequency: str) -> list:
        log.debug(f"Start date: {date_start}. End date: {date_end}")

        dates = (
            pandas.date_range(
                date_start,
                date_end,
                freq=frequency,
                tz="Asia/Taipei",
            ).strftime(YYYYMMDD).tolist()
        )
        return dates

    @staticmethod
    @interceptor
    def today(fmt: str) -> str:
        return datetime.now().strftime(fmt)

    @staticmethod
    @interceptor
    def strformat(date: str, oldFmt: str, newFmt: str) -> str:
        return datetime.strptime(date, oldFmt).strftime(newFmt)
