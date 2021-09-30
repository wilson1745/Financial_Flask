# -*- coding: UTF-8 -*-
import traceback

import calculations.core
import calculations.repository
from calculations.common.exceptions.core_exception import CoreException
from calculations.core import LOG
from calculations.repository.dailyfund_repo import DailyFundRepo

if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    try:
        stock = DailyFundRepo.find_by_symbol('B09%2C012')
        LOG.debug(stock)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
