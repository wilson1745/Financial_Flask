import multiprocessing
from datetime import datetime
from pathlib import Path

from calculations.common.constants.constants import INIT
from calculations.core import log

""" Top level than other modules in core package """
PATH = (str(Path(Path(__file__).resolve().parents[1])) + r"\files\logs")
# Check if this directory is exist
Path(PATH).mkdir(parents=True, exist_ok=True)

LOG = log.Logger((PATH + r"\%s.log") % datetime.now().strftime('%Y_%m_%d'), level='debug').logger
LOG.info(f"Initialize Log.Logger: {LOG}")

""" For parallel process (Do not use all my processing power) """
# CPU_THREAD = multiprocessing.cpu_count()
CPU_THREAD = multiprocessing.cpu_count() - 1
LOG.info(f"Initialize CPU_THREAD: {CPU_THREAD} ")

if __name__ == '__main__':
    LOG.info(f"Calculations Core {INIT} 作為主程序啟動")
else:
    LOG.info(f"Calculations Core {INIT} 初始化")
