from application import jsonrpc,db
from .marshmallow import MobileSchema,UserSchema
from marshmallow import ValidationError

from message import ErrorMessage as Message
from status import APIStatus as status

# rpc接口 校验手机号
@jsonrpc.method("User.mobile")
def mobile(mobile):
    # 验证手机号码是否已经注册
    ms = MobileSchema()
    try:
        ms.load({"mobile":mobile})
        ret = {"errno":status.CODE_OK, "errmsg":Message.ok}
    except ValidationError as e:
        ret = {"error":status.CODE_VALIDATE_ERROR,"errmsg":e.messages["mobile"][0]}
    return ret

# 提交注册信息
@jsonrpc.method("User.register")
def register(mobile,password,password2,sms_code):
    """用户信息注册"""
    try:
        ms = MobileSchema()
        ms.load({"mobile":mobile})
        us = UserSchema()
        # 校验并保存
        user = us.load({
            "mobile":mobile,
            "password": password,
            "password2": password2,
            "sms_code": sms_code
        })
        data = {"errno": status.CODE_OK, "errmsg": us.dump(user)}
    except ValidationError as e:
        data = {"errno": status.CODE_VALIDATE_ERROR, "errmsg": e.messages}
    return data







