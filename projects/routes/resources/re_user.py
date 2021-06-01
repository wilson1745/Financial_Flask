import traceback

from flask import current_app as app, request
from flask_restful import Resource

from projects.common import constants
from projects.common.exceptions.core_exception import CoreException
from projects.common.utils.resp_utils import Response
from projects.models.schema.user_schema import UserSchema
from projects.models.user_model import UserModel
from projects.routes import log

user_schema = UserSchema(many=False)
user_schemass = UserSchema(many=True)


class User(Resource):

    @staticmethod
    def get(name):
        try:
            user = UserModel.get_user(name)
            result = user_schema.dump(user)
            log.debug(f"UserModel.get_user(name): {result}")
            if not user:
                return Response.warn(message=constants.DATA_NOT_EXIST % name, code=403)

            return Response.ok('', result)
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            return Response.fail(str(e))

    @staticmethod
    def post(name):
        try:
            result = user_schema.load(request.json)

            if len(result.errors) > 0:
                return result.errors, 433

            user = UserModel(name, result.data['email'], result.data['password'])
            user.add_user()

            return Response.ok('Insert user success', user_schema.dump(user).data)
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            return Response.fail(str(e))

    @staticmethod
    def put(name):
        try:
            result = user_schema.load(request.json)
            if len(result.errors) > 0:
                return result.errors, 433

            user = UserModel.get_user(name)
            if not user:
                return Response.warn(message=constants.DATA_NOT_EXIST % name, code=403)

            user.email = result.data['email']
            user.password = result.data['password']

            return Response.ok('Update user success', user_schema.dump(user).data)
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            return Response.fail(str(e))

    @staticmethod
    def delete(name):
        try:
            UserModel.delete_user(name)
            return {
                'message': 'Delete done!'
            }
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            return Response.fail(str(e))


class Users(Resource):

    def get(self):
        try:
            result = user_schemass.dump(UserModel.get_all_user())
            app.logger.debug(f"Users: {hex(id(app.logger))}")
            app.logger.debug(f"get(self):{result}")
            # self.logger.debug(f"Users: {hex(id(self.logger))}")
            # self.logger.debug(f"get(self):{result}")

            return Response.ok('', result)
        except Exception as e:
            CoreException.show_error(e, traceback.format_exc())
            return Response.fail(str(e))
