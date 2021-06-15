from datetime import datetime
from pathlib import Path

from calculations.core import Log

""" Top level than other modules in core package """
log = Log.Logger((str(Path(Path(__file__).resolve().parents[0])) + r"\files\logs\%s.log")
                 % datetime.now().strftime("%Y_%m_%d"), level="debug").logger
log.info("Initiallize calculations logger completely")

if __name__ == "__main__":
    log.info("calculations 作為主程序啟動")
else:
    log.info("calculations 初始化")
