from flask import current_app as app

from flask_restful import Resource


class PrintHelloWorld(Resource):

    @staticmethod
    def get():
        """ Test if the flask is working or not """
        app.logger.debug("PrintHelloWorld static method....")

        return {
                   'message': 'Hello Wrold!'
               }, 200
