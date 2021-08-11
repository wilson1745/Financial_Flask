# -*- coding: UTF-8 -*-
from datetime import datetime

import pandas

from calculations import LOG
from calculations.common.utils import constants


class DateUtils:
    """ Tools for date """

    def __init__(self):
        """ Constructor """
        pass

    @staticmethod
    def list_date(date_start: str, date_end: str, freq: str) -> list:
        """ List date from start to end """
        LOG.debug(f"Start date: {date_start}. End date: {date_end}")

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
        """ Get today's date as string """
        return datetime.now().strftime(date_format)

    @staticmethod
    def str_fmt(date: str, oldFormat: str, newFormat: str) -> str:
        """ Format string date from old to new """
        return datetime.strptime(date, oldFormat).strftime(newFormat)

    @staticmethod
    def datetime_fmt(date: datetime, fmt: str) -> str:
        """ Format datetime to string """
        return datetime.strftime(date, fmt)

    @classmethod
    def default_msg(cls, fmt: str) -> str:
        """ Default today's header for line notify """
        return f"\n-------({cls.today(fmt)})-------\n"
