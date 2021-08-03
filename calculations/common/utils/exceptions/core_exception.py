import os

from calculations import LOG


class CoreException:
    """ Custom Exception """

    def __init__(self):
        pass

    @staticmethod
    def show_error(e: Exception, trace: str):
        LOG.error(f"Exception: {e}")
        LOG.error(f'Exception: {trace}')

    @staticmethod
    def show(get_result):
        LOG.debug("Callback: {} PID: {}".format(get_result, os.getpid()))

    @staticmethod
    def error(value):
        LOG.error("error: {}".format(value))
