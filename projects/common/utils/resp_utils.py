import logging

from projects.common import constants
from projects.common.interceptor import interceptor

log = logging.getLogger(constants.LOG_PROJECTS)


class Response:

    @staticmethod
    @interceptor
    def ok(message: str, result):
        """ Return successful message and result"""
        return {
                   'message': message,
                   'result': result
               }, 200

    @staticmethod
    @interceptor
    def warn(message: str, code: int):
        """ Return warning or fail message """
        return {
                   'message': message
               }, code

    @staticmethod
    @interceptor
    def fail(message: str):
        """ Return exception message """
        return {
            'Exception message': message
        }
