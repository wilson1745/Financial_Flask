from datetime import datetime
from pathlib import Path

from calculations.core import Log

""" Top level than other modules in core package """
LOG = Log.Logger((str(Path(Path(__file__).resolve().parents[1])) + r"\files\logs\%s.log")
                 % datetime.now().strftime("%Y_%m_%d"), level="debug").logger
LOG.info("Initiallize Interceptor's LOG completely")

if __name__ == "__main__":
    LOG.info("core 作為主程序啟動")
else:
    LOG.info("core 初始化")
