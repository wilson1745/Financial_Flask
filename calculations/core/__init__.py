# import multiprocessing
# from datetime import datetime
# from pathlib import Path
#
# from calculations.core import Log
#
# """ Top level than other modules in core package """
# LOG = Log.Logger((str(Path(Path(__file__).resolve().parents[1])) + r"\files\logs\%s.log")
#                  % datetime.now().strftime("%Y_%m_%d"), level="debug").logger
# LOG.info(f"Initiallize Log.Logger: {LOG}")
#
# """ For parallel process (Do not use all my processing power) """
# # CPU_THREAD = multiprocessing.cpu_count()
# CPU_THREAD = multiprocessing.cpu_count() - 1
# LOG.info(f"Initiallize cpu_thread: {CPU_THREAD} ")
#
# if __name__ == '__main__':
#     LOG.info("Project Calculations 作為主程序啟動")
# else:
#     LOG.info("Project Calculations 初始化")
