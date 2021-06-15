import logging
import os

log = logging.getLogger('projects')


class CoreException:
    """ Custom Exception """

    def __init__(self):
        pass

    # @interceptor
    @staticmethod
    def show_error(e: Exception, trace: str):
        log.error(f"Exception: {e}")
        log.error(f'Exception: {trace}')

    # @interceptor
    @staticmethod
    def show(get_result):
        log.debug("Callback: {} PID: {}".format(get_result, os.getpid()))

    # @interceptor
    @staticmethod
    def error(value):
        log.error("error: {}".format(value))
