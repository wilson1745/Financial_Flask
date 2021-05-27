import traceback

from flask import Blueprint

from projects.models.schema.user_schema import UserSchema
from projects.models.user_model import UserModel
from projects.common.exceptions.core_exception import CoreException
from projects.resources import log

"""藍圖物件可看做一個縮小版的app物件"""
bp = Blueprint('user_bp', __name__)  # 第一個引數為藍圖名稱，隨便取

user_schema = UserSchema(many=False)


@bp.route('/user_bp/<string:name>')
def userget(name):
    try:
        # name = "haha"
        data = UserModel.get_user(name)
        result = user_schema.dump(data)
        log.debug(f"UserModel.get_user(name): {result}")
        if not data:
            return {
                       'message': 'username not exist!'
                   }, 403

        return {
            'message': '',
            'user': result
        }
    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())
        return {
            "Exception message": str(e)
        }
