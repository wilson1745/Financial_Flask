# -*- coding: UTF-8 -*-
from datetime import datetime

import pandas

from calculations import log
from calculations.common.utils import constants


class DateUtils:
    """ Tools for date """

    @staticmethod
    def getDateList(date_start: str, date_end: str, freq: str) -> list:
        log.debug(f"Start date: {date_start}. End date: {date_end}")

        dates = (
            pandas.date_range(
                date_start,
                date_end,
                freq=freq,
                tz="Asia/Taipei",
            ).strftime(constants.YYYYMMDD).tolist()
        )
        return dates

    @staticmethod
    def today(date_format: str = constants.YYYYMMDD_HHMMSS) -> str:
        return datetime.now().strftime(date_format)

    @staticmethod
    def strformat(date: str, oldFormat: str, newFormat: str) -> str:
        return datetime.strptime(date, oldFormat).strftime(newFormat)

    @classmethod
    def default_msg(cls, fmt: str) -> str:
        return f"\n--------({cls.today(fmt)})--------\n"
