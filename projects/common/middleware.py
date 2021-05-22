""" MiddleWare with HTTP protocol """
import logging
import traceback

from projects.common.exception.core_exception import CoreException

log = logging.getLogger("projects")


class MiddleWare(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """
        environ：包含了客户端請求的信息以及其他信息
        start_response：要響應返還的接口
        """
        path = environ['werkzeug.request']
        log.info(f"====== Start {path} ======")

        try:
            return self.app(environ, start_response)
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
        finally:
            log.info(f"====== End {path} ======")
