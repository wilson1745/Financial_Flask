# -*- coding: UTF-8 -*-
import multiprocessing
import os
import sys
import time
import traceback
from multiprocessing.pool import ThreadPool

import pandas as pd

sys.path.append("C:\\Users\\wilso\\PycharmProjects\\Financial_Flask")

from calculations import log
from calculations.common.utils import constants
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_dailyfund import FundGroup
from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.common.utils.file_utils import FileUtils
from calculations.core.Interceptor import interceptor
from calculations.repository import dailyfund_repo, itemfund_repo
from calculations.resources import line_notify


@interceptor
def main(group: FundGroup):
    """ Grab history data """
    try:
        date = DateUtils.today(constants.YYYYMMDD)
        log.info(f"start ({DateUtils.today()}): {date}")

        item_df = itemfund_repo.findAll()
        if item_df.empty:
            log.warning(f"itemfund_repo.findAll() is None")
        else:
            pools = ThreadPool(multiprocessing.cpu_count() - 1)
            """ Daily or Range """
            df_list = pools.map(func=FileUtils.fundHtmlDaily if group is FundGroup.DAILY else FileUtils.fundHtmlRange,
                                iterable=item_df.itertuples())
            df = pd.concat(df_list)

            if not df.empty:
                # log.debug(df)
                """ Daily or Range """
                dailyfund_repo.checkAndSave(list(df.itertuples())) if group is FundGroup.DAILY else dailyfund_repo.saveToDbBatch(df.values.tolist())
            else:
                log.warning(constants.DATA_NOT_EXIST)
        log.info(f"end ({DateUtils.today()}): {date}")
    except Exception:
        raise


if __name__ == "__main__":
    """ ------------------- App Start ------------------- """
    now = time.time()
    ms = DateUtils.default_msg(constants.YYYYMMDD_SLASH)
    fileName = os.path.basename(__file__)

    try:
        main(FundGroup.DAILY)
        # main(FundGroup.RANGE)
        line_notify.sendMsg([ms, constants.SUCCESS % fileName], constants.TOKEN_NOTIFY)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        line_notify.sendMsg([ms, constants.FAIL % fileName], constants.TOKEN_NOTIFY)
    finally:
        log.debug(f"Time consuming: {time.time() - now}")
        log.debug(f"End of {fileName}")
