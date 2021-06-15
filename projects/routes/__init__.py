""" contains logic for """
import logging
import os

from projects.common import constants

log = logging.getLogger(constants.LOG_PROJECTS)

if __name__ == '__main__':
    log.info(f'{os.path.dirname(__file__)} 作為主程序啟動')
else:
    log.info(f'{os.path.dirname(__file__)} 初始化')
