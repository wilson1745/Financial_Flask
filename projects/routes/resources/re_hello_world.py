from flask import current_app as app
from flask_restful import Resource

from projects.common.utils.resp_utils import Response


class PrintHelloWorld(Resource):

    @staticmethod
    def get():
        """ Test if the flask is working or not """
        app.logger.debug('PrintHelloWorld static method....')

        return Response.ok('Hello Wrold!', None)
