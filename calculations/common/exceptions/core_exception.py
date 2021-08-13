import os

from calculations.core import LOG


class CoreException:
    """ Custom Exception """

    def __init__(self):
        """ Constructor """
        pass

    @staticmethod
    def show_error(e: Exception, trace: str):
        """ show_error """
        LOG.error(f"\nException: {e} \nTraceBack: {trace}")

    @staticmethod
    def show_warn(e: Exception, trace: str):
        """ show_warn """
        LOG.warning(f"\nWarning: {e} \nTraceBack: {trace}")

    @staticmethod
    def show(get_result):
        """ show """
        LOG.debug("Callback: {} PID: {}".format(get_result, os.getpid()))

    @staticmethod
    def error(value):
        """ error """
        LOG.error("error: {}".format(value))
