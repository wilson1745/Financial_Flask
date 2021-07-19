import os

from calculations import log


class CoreException:
    """ Custom Exception """

    def __init__(self):
        pass

    @staticmethod
    def show_error(e: Exception, trace: str):
        log.error(f"Exception: {e}")
        log.error(f'Exception: {trace}')

    @staticmethod
    def show(get_result):
        log.debug("Callback: {} PID: {}".format(get_result, os.getpid()))

    @staticmethod
    def error(value):
        log.error("error: {}".format(value))
