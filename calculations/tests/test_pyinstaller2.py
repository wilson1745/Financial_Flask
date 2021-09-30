# -*- coding: UTF-8 -*-
import traceback
import calculations.core
import calculations.repository

from calculations.common.exceptions.core_exception import CoreException
from calculations.resources.dailyfund_notify import DailyFundNotify

if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    try:
        DailyFundNotify.main()
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
