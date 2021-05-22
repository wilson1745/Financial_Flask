""" 預期請求參數的內容的基本結構 """
from marshmallow import fields

from projects.common.ma import ma_marshmallow


class UserSchema(ma_marshmallow.Schema):
    id = fields.Integer()
    name = fields.Str()
    email = fields.Email()
    password = fields.Str()

    # class Meta(ma.Schema.Meta):
    # model = UserModel
