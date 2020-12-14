from application import jsonrpc, db
from .marshmallow import MobileSchema, UserSchema
from marshmallow import ValidationError

from message import ErrorMessage as Message
from status import APIStatus as status


# rpc接口 校验手机号
@jsonrpc.method("User.mobile")
def mobile(mobile):
    # 验证手机号码是否已经注册
    ms = MobileSchema()
    try:
        ms.load({"mobile": mobile})
        ret = {"errno": status.CODE_OK, "errmsg": Message.ok}
    except ValidationError as e:
        ret = {"error": status.CODE_VALIDATE_ERROR, "errmsg": e.messages["mobile"][0]}
    return ret


# 提交注册信息
@jsonrpc.method("User.register")
def register(mobile, password, password2, sms_code):
    """用户信息注册"""
    try:
        ms = MobileSchema()
        ms.load({"mobile": mobile})
        us = UserSchema()
        print("11111111111111")
        print(mobile,password,password2,sms_code)
        # 校验并保存
        user = us.load({
            "mobile": mobile,
            "password": password,
            "password2": password2,
            "sms_code": sms_code
        })
        data = {"errno": status.CODE_OK, "errmsg": us.dump(user)}
    except ValidationError as e:
        data = {"errno": status.CODE_VALIDATE_ERROR, "errmsg": e.messages}
    return data


# 登录
from flask_jwt_extended import create_access_token, \
    create_refresh_token, jwt_required, get_jwt_identity, \
    jwt_refresh_token_required
from flask import jsonify, json

from sqlalchemy import or_
from .models import User
from message import ErrorMessage as message
from status import APIStatus as status

from flask import current_app, request
from urllib.parse import urlencode
from urllib.request import urlopen


@jsonrpc.method("User.login")
def login(ticket, randstr, account, password):
    """根据用户登录信息生成token"""
    # 校验防水墙验证码
    print("randstr", randstr)
    params = {
        "aid": current_app.config.get("CAPTCHA_APP_ID"),
        "AppSecretKey": current_app.config.get("CAPTCHA_APP_SECRET_KEY"),
        "Ticket": ticket,
        "Randstr": randstr,
        "UserIP": request.remote_addr
    }
    print("**************8")
    print(current_app.config.get("CAPTCHA_APP_ID"))
    print(current_app.config.get("CAPTCHA_APP_SECRET_KEY"))
    print(ticket)
    print(randstr)
    print(request.remote_addr)
    print("**************8")
    # 把字典数据转换成地址栏的查询字符串格式
    # aid=xxx&AppSecretKey=xxx&xxxxx
    params = urlencode(params)
    url = current_app.config.get("CAPTCHA_GATEWAY")
    # 发送http的get请求
    # print("%s?%s" % (url, params))
    f = urlopen("%s?%s" % (url, params))
    # https://ssl.captcha.qq.com/ticket/verify?aid=xxx&AppSecretKey=xxx&xxxxx

    content = f.read()
    res = json.loads(content)
    print("**********-------------")
    print(res)

    if int(res.get("response")) != 1:
        # 验证失败
        return {"errno": status.CODE_CAPTCHA_ERROR, "errmsg": message.captcaht_no_match}

    # 1. 根据账户信息和密码获取用户
    if len(account) < 1:
        return {"errno": status.CODE_NO_ACCOUNT, "errmsg": message.account_no_data}
    print("***************--------------",account)
    user = User.query.filter(or_(
        User.mobile == account,
        User.email == account,
        User.name == account
    )).first()
    print("**************+++++++++++++",user)
    if user is None:
        return {"errno": status.CODE_NO_USER, "errmsg": message.user_not_exists}

    # 验证密码
    if not user.check_password(password):
        return {"errno": status.CODE_PASSWORD_ERROR, "errmsg": message.password_error}

    # 2. 生成jwt token
    # 没有获取用户信息的时候,先看了下是否生成了token
    # access_token = create_access_token(identity=account)
    # refresh_token = create_refresh_token(identity=account)

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    print("********* token值 **********")
    # 登录成功获返回access_token和refresh_token,refresh_token不生成token
    # 只是调用access 通过 access_token生成token,
    print("access_token", access_token)
    print("refresh_token", refresh_token)
    print("****************************")
    # return "ok"

    return {"errno": status.CODE_OK, "errmsg": message.ok, "access_token": access_token, "refresh_token": refresh_token}


from .marshmallow import UserInfoSchema


@jsonrpc.method("User.info")
@jwt_required  # 验证jwt
def info():
    """获取用户信息"""
    current_user_id = get_jwt_identity()  # get_jwt_identity 用于获取载荷中的数据
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }
    uis = UserInfoSchema()
    data = uis.dump(user)
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "is_set_transaction_password":bool(user.transaction_password),
        **data
    }

    # user_data = json.loads(get_jwt_identity())  # get_jwt_identity 用于获取载荷中的数据
    # print(user_data)
    # return "ok"


@jsonrpc.method("User.refresh")
@jwt_refresh_token_required
def refresh():
    """重新获取新的认证令牌token"""
    current_user = get_jwt_identity()
    # 重新生成token
    access_token = create_access_token(identity=current_user)
    return access_token


# 更改头像
import base64, uuid, os
from application import mongo
from datetime import datetime


@jsonrpc.method("User.avatar.update")
@jwt_required  # 验证jwt
def update_avatar(avatar):
    print("******** avatar ********")
    print(avatar)
    print("************************")
    """更新用户头像"""
    # 1. 接受客户端上传的头像信息
    ext = avatar[avatar.find("/") + 1:avatar.find(";")]  # 资源格式
    b64_avatar = avatar[avatar.find(",") + 1:]  # 图片信息
    b64_image = base64.b64decode(b64_avatar)
    filename = uuid.uuid4()
    static_path = os.path.join(current_app.BASE_DIR, current_app.config["STATIC_DIR"])
    print(static_path)
    print("%s/%s.%s" % (static_path, filename, ext))
    with open("%s/%s.%s" % (static_path, filename, ext), "wb") as f:
        f.write(b64_image)

    # return "ok"
    current_user_id = get_jwt_identity()
    print("***** current_user_id ******")
    print(current_user_id)
    print("****************************")
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }
    user.avatar = "%s.%s" % (filename, ext)
    db.session.commit()

    # 添加修改记录!
    document = {
        "user_id": user.id,
        "user_name": user.name,
        "user_nickname": user.nickname,
        "update_time": datetime.now().timestamp(),
        "avatar": avatar,  # 图片内容
        "type": "avatar",  # 本次操作的类型
    }
    mongo.db.user_info_history.insert_one(document)

    return {
        "errno": status.CODE_OK,
        "errmsg": message.avatar_save_success,
        "avatar": "%s.%s" % (filename, ext)
    }


from flask import make_response, request


@jwt_required  # 验证jwt
def avatar():
    """获取头像信息"""
    avatar = request.args.get("sign")
    ext = avatar[avatar.find(".") + 1:]
    filename = avatar[:avatar.find(".")]
    static_path = os.path.join(current_app.BASE_DIR, current_app.config["STATIC_DIR"])
    with open("%s/%s.%s" % (static_path, filename, ext), "rb") as f:
        content = f.read()
    response = make_response(content)
    response.headers["Content-Type"] = "image/%s" % ext
    return response



@jsonrpc.method("User.check")
@jwt_required  # 验证jwt
def check():
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
    }


@jsonrpc.method("User.refresh")
@jwt_refresh_token_required  # 验证refresh_token
def refresh():
    """重新获取新的认证令牌token"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    """重新生成token"""
    access_token = create_access_token(identity=current_user_id)
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "access_token": access_token
    }


@jsonrpc.method("User.transaction.password")
@jwt_required # 验证jwt
def transaction_password(password1, password2,old_password=None):
    """
    交易密码的初始化和修改
    1. 刚注册的用户，没有交易密码，所以此处填写的是新密码
    2. 已经有了交易密码的用户，修改旧的交易密码
    """

    if password1 != password2:
        return {
            "errno": status.CODE_TRANSACTION_PASSWORD_ERROR,
            "errmsg": message.transaction_password_not_match
        }

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    # 如果之前有存在交易密码，则需要验证旧密码
    if user.transaction_password:
        """修改"""
        # 验证旧密码
        ret = user.check_transaction_password(old_password)
        if ret == False:
            return {
                "errno": status.CODE_PASSWORD_ERROR,
                "errmsg": message.transaction_password_error
            }

    """设置交易密码"""
    user.transaction_password = password1
    db.session.commit()

    # 添加交易密码的修改记录，为了保证安全，仅仅记录旧密码！
    if old_password:
        document = {
            "user_id": user.id,
            "user_name": user.name,
            "user_nikcname": user.nickname,
            "updated_time": datetime.now().timestamp(),        # 修改时间
            "transaction_password": old_password, # 变更内容
            "type": "transaction_password",    # 本次操作的类型
        }
        mongo.db.user_info_history.insert_one(document)

    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok
    }

@jsonrpc.method("User.update.password")
@jwt_required
def update_password(old_password, new_password):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    # 验证密码
    if not user.check_password(old_password):
        return {"errno": status.CODE_PASSWORD_ERROR, "errmsg": message.password_error}

    if old_password == new_password:
        return {
            "errno": status.CODE_OLD_NEW_PASSWORD_MATCH,
            "errmsg": message.old_new_password_match
        }

    # 添加交易密码的修改记录，为了保证安全，仅仅记录旧密码！
    if old_password:
        document = {
            "user_id": user.id,
            "user_name": user.name,
            "user_nikcname": user.nickname,
            "updated_time": datetime.now().timestamp(),  # 修改时间
            "transaction_password": old_password,  # 变更内容
            "type": "transaction_password",  # 本次操作的类型
        }
        mongo.db.user_info_history.insert_one(document)
    if new_password:
        print("********************************")
        print(user.password)
        # user.password = user.password
        # ret = User.query.get(user.id).update({User._password:user.password})
        user.password = new_password
        db.session.commit()
        print("*****************8")
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok
    }


@jsonrpc.method("User.update.nickname")
@jwt_required
def update_nickname(nickname):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    # 添加交易密码的修改记录，为了保证安全，仅仅记录旧密码！
    if nickname:
        document = {
            "user_id": user.id,
            "user_name": user.name,
            "user_nikcname": user.nickname,
            "updated_time": datetime.now().timestamp(),  # 修改时间
            "type": "update_nickname",  # 本次操作的类型
        }
        mongo.db.user_info_history.insert_one(document)
    if nickname:
        print("*****************8")
        print(user.nickname)
        user.nickname = nickname
        db.session.commit()
        print("*****************8")
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "nickname": nickname
    }
