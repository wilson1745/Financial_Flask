import traceback

from flask import Blueprint

from projects.common import constants
from projects.common.exceptions.core_exception import CoreException
from projects.common.utils.resp_utils import Response
from projects.models.schema.user_schema import UserSchema
from projects.models.user_model import UserModel
from projects.routes import log

"""藍圖物件可看做一個縮小版的app物件"""
user_bp = Blueprint('user_bp', __name__)  # 第一個引數為藍圖名稱，隨便取

user_schema = UserSchema(many=False)


@user_bp.route('/user_bp/<string:name>')
def userget(name):
    try:
        data = UserModel.get_user(name)
        result = user_schema.dump(data)
        log.debug(f'UserModel.get_user(name): {result}')
        if not data:
            return Response.warn(message=constants.DATA_NOT_EXIST % name, code=403)

        return Response.ok('', result)
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        return Response.fail(str(e))
