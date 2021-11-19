import platform
import multiprocessing
from datetime import datetime
from pathlib import Path

from calculations.common.constants.constants import INIT
from calculations.core import log

system_os = platform.system()
try:
    SLASH = ""
    if system_os == 'Windows':
        SLASH = "\\"
    elif system_os == 'Darwin':
        SLASH = "\\"
    elif system_os == 'Linux':
        SLASH = "/"
    else:
        raise Exception(f"Unknown system: {system_os}")

    """ Top level than other modules in core package """
    # r"\files\logs" or r"/files/logs"
    PATH = (str(Path(Path(__file__).resolve().parents[1])) + SLASH + "files" + SLASH + "logs")
    # Check if this directory is exist
    Path(PATH).mkdir(parents=True, exist_ok=True)

    # r"\%s.log" or r"/%s.log"
    LOG = log.Logger((PATH + SLASH + r"%s.log") % datetime.now().strftime('%Y_%m_%d'), level='debug').logger
    LOG.info(f"Initialize Log.Logger: {LOG}")

    """ For parallel process (Do not use all my processing power) """
    # CPU_THREAD = multiprocessing.cpu_count()
    CPU_THREAD = multiprocessing.cpu_count() - 1
    LOG.info(f"Initialize CPU_THREAD: {CPU_THREAD} ")
except Exception as e:
    raise Exception(f"Unknown system: {system_os}")

# """ Top level than other modules in core package """
# PATH = (str(Path(Path(__file__).resolve().parents[1])) + r"\files\logs")
# # Check if this directory is exist
# Path(PATH).mkdir(parents=True, exist_ok=True)
#
# LOG = log.Logger((PATH + r"\%s.log") % datetime.now().strftime('%Y_%m_%d'), level='debug').logger
# LOG.info(f"Initialize Log.Logger: {LOG}")
#
# """ For parallel process (Do not use all my processing power) """
# # CPU_THREAD = multiprocessing.cpu_count()
# CPU_THREAD = multiprocessing.cpu_count() - 1
# LOG.info(f"Initialize CPU_THREAD: {CPU_THREAD} ")

if __name__ == '__main__':
    LOG.info(f"Calculations Core {INIT} 作為主程序啟動")
else:
    LOG.info(f"Calculations Core {INIT} 初始化")
