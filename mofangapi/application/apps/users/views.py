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
def register(mobile, password, password2, sms_code, invite_uid):
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
            "sms_code": sms_code,
            "invite_uid": invite_uid,
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

    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "id": user.id,
        "nickname": user.nickname if user.nickname else account,
        "avatar": user.avatar if user.avatar else current_app.config["DEFAULT_AVATAR"],
        "money": float(user.money) if user.money else 0,
        "credit": float(user.credit) if user.credit else 0,
        "access_token": access_token,
        "refresh_token": refresh_token}


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

# 修改手机号
@jsonrpc.method("User.transaction.phone")
@jwt_required
def update_phone(password, phone, phone_code):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    print("**********************")
    print(user)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    # 验证密码
    if not user.check_password(password):
        return {"errno": status.CODE_PASSWORD_ERROR, "errmsg": message.password_error}

    import redis
    # todo 校验短信验证码
    # 1. 从redis中提取验证码
    redis_sms_code = redis.get("sms_%s" % (phone))
    # 如果从redis_sms_code 没取到值返回错误信息
    if redis_sms_code is None:
        print("redis验证码为空错误")
        raise ValidationError(massage=Message.sms_code_expired, field_name="sms_code")
    redis_sms_code = redis_sms_code.decode()
    # 2. 从客户端提交的数据data中提取验证码
    sms_code = phone
    # 3. 字符串比较,如果失败,抛出异常,否则,直接删除验证码
    if sms_code != redis_sms_code:
        print("验证码校验错误")
        raise ValidationError(message=Message.sms_code_error, field_name="sms_code")
    redis.delete("sms_%s" % (phone))
    # print(data["sms_code"])
    # if data["sms_code"] != redis.get("sms_%s" %data["mobile"]).decode():
    #     raise ValidationError(message=Message.sms_not_match,field_name="sms_code")


    if phone:

        document = {
            "user_id": user.id,
            "user_name": user.name,
            "user_nikcname": user.nickname,
            "updated_time": datetime.now().timestamp(),  # 修改时间
            "transaction_phone": phone,  # 变更内容
            "type": "transaction_phone",  # 本次操作的类型
        }

        # mongo.db.user_info_history.insert_one(document)

        # user.password = user.password
        # ret = User.query.get(user.id).update({User._password:user.password})
        user.mobile = phone
        db.session.commit()


    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok
    }



# 添加好友 搜索
from sqlalchemy import or_
from .models import UserRelation
from .marshmallow import UserSearchInfoSchema as usis
@jsonrpc.method("User.user.relation")
@jwt_required # 验证jwt
def user_relation(account):
    """搜索用户信息"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    # 1. 识别搜索用户
    receive_user_list = User.query.filter( or_(
        User.mobile == account,
        User.name == account,
        User.nickname.contains(account),
        User.email==account
    ) ).all()

    if len(receive_user_list) < 1:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.receive_user_not_exists,
        }
    # context 可用于把视图中的数据传递给marshmallow转换器中使用
    marshmallow = usis(many=True,context={"user_id": user.id})
    user_list = marshmallow.dump(receive_user_list)
    print(">>>> 1")
    print(user_list)
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "user_list": user_list
    }

# 申请添加好友
@jsonrpc.method("User.friend.add")
@jwt_required
def add_friend_apply(user_id):
    """申请添加好友"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    receive_user = User.query.get(user_id)
    if receive_user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.receive_user_not_exists,
        }

    # 查看是否被对方拉黑了

    # 添加一个申请记录
    document = {
        "send_user_id": user.id,
        "send_user_nickname": user.nickname,
        "send_user_avatar": user.avatar,
        "receive_user_id": receive_user.id,
        "receive_user_nickname": receive_user.nickname,
        "receive_user_avatar": receive_user.avatar,
        "time": datetime.now().timestamp(),  # 操作时间
        "status": 0,
    }
    mongo.db.user_relation_history.insert_one(document)
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
    }

# 处理好友请求
from sqlalchemy import and_
@jsonrpc.method("User.friend.apply")
@jwt_required # 验证jwt
def add_friend_apply(user_id,agree,search_text):
    """处理好友申请"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    receive_user = User.query.get(user_id)
    if receive_user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.receive_user_not_exists,
        }

    relaionship = UserRelation.query.filter(
        or_(
            and_(UserRelation.send_user == user.id, UserRelation.receive_user == receive_user.id),
            and_(UserRelation.receive_user == user.id, UserRelation.send_user == receive_user.id),
        )
    ).first()

    if agree:
        if receive_user.mobile == search_text:
            chioce = 0
        elif receive_user.name == search_text:
            chioce = 1
        elif receive_user.email== search_text:
            chioce = 2
        elif receive_user.nickname == search_text:
            chioce = 3
        else:
            chioce = 4

        if relaionship is not None:
            relaionship.relation_status = 1
            relaionship.relation_type = chioce
            db.session.commit()
        else:
            relaionship = UserRelation(
                send_user=user.id,
                receive_user=receive_user.id,
                relation_status=1,
                relation_type=chioce,
            )
            db.session.add(relaionship)
            db.session.commit()

    # 调整mongoDB中用户关系的记录状态
    query = {
        "$or": [{
            "$and": [
                {
                    "send_user_id": user.id,
                    "receive_user_id": receive_user.id,
                    "time": {"$gte": datetime.now().timestamp() - 60 * 60 * 24 * 7}
                }
            ],
        }, {
            "$and": [
                {
                    "send_user_id": receive_user.id,
                    "receive_user_id": user.id,
                    "time": {"$gte": datetime.now().timestamp() - 60 * 60 * 24 * 7}
                }
            ],
        }]
    }
    if agree:
        argee_status = 1
    else:
        argee_status = 2

    ret = mongo.db.user_relation_history.update(query, {"$set":{"status":argee_status}})
    if ret and ret.get("nModified") < 1:
        return {
            "errno": status.CODE_UPDATE_USER_RELATION_ERROR,
            "errmsg": message.update_user_relation_fail,
        }
    else:
        return {
            "errno": status.CODE_OK,
            "errmsg": message.update_success,
        }

# 添加好友时，直接获取与当前用户存在申请好友历史的所有记录.
@jsonrpc.method("Use.relation.history")
@jwt_required # 验证jwt
def history_relation():
    """查找好友关系历史记录"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    query = {
        "$or":[
            {"send_user_id":user.id,"time": {"$gte": datetime.now().timestamp() - 60 * 60 * 24 * 7}},
            {"receive_user_id": user.id,"time": {"$gte": datetime.now().timestamp() - 60 * 60 * 24 * 7}},
        ]
    }
    document_list = mongo.db.user_relation_history.find(query,{"_id":0})
    data_list = []
    for document in document_list:
        if document.get("send_user_id") == user.id and document.get("status") == 0:
            document["status"] = (0,"已添加")
        elif document.get("receive_user_id") == user.id and document.get("status") == 0:
            document["status"] = (0, "等待通过")
        elif document.get("status") == 1:
            document["status"] = (1, "已通过")
        else:
            document["status"] = (2, "已拒绝")

        data_list.append(document)

    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "data_list": data_list,
    }


# 好友列表
@jsonrpc.method("User.friend.list")
@jwt_required # 验证jwt
def list_friend(page=1,limit=2):
    """好友列表"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    pagination = UserRelation.query.filter(
        or_(
            and_(UserRelation.send_user == user.id),
            and_(UserRelation.receive_user == user.id),
        )
    ).paginate(page,per_page=limit)

    print("**************************")
    print("用户分页数据",pagination)
    print("**************************")
    user_id_list = []
    for relation in pagination.items:
        print("---------------")
        print("用户分页数据的每一个发送用户", relation.send_user)
        print("user.id                 ", user.id)
        print("---------------")
        if relation.send_user == user.id:
            user_id_list.append(relation.receive_user)
        else:
            user_id_list.append(relation.send_user)

    # 获取用户详细信息
    user_list = User.query.filter(User.id.in_(user_id_list)).all()
    friend_list = [{"avatar":user.avatar,"nickname":user.nickname,"id":user.id,"fruit":0,"fruit_status":0} for user in user_list]
    pages = pagination.pages
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "friend_list": friend_list,
        "pages": pages
    }



# 生成二维码
from application import QRCode
from flask import make_response,request
@jwt_required
def invite_code():
    """"邀请好友的二维码"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "error": status.CODE_NO_USER,
            "errmsg":message.user_not_exists,
        }
    static_path = os.path.join(current_app.BASE_DIR, current_app.config["STATIC_DIR"])
    if not user.avatar:
        user.avatar =  current_app.config["DEFAULT_AVATAR"]

    avatar = static_path + "/" + user.avatar
    print("邀请码相关,头像路径")
    data = current_app.config.get("SERVER_URL",request.host_url[:-1]) + "/users/invite/download?uid=%s" % current_user_id

    image = QRCode.qrcode(data, box_size=16, icon_img=avatar)
    b64_image = image[image.find(",") + 1:]
    qrcode_iamge = base64.b64decode(b64_image)
    response = make_response(qrcode_iamge)
    response.headers["Content-Type"] = "image/png"
    return response


from flask import render_template
def invite_download():
    uid = request.args.get("uid")
    if "micromessenger" in request.headers.get("User-Agent").lower():
        position = "weixin"
    else:
        position = "other"

    return render_template("users/download.html",position=position,uid=uid)

from application import jsonrpc
from .models import Recharge
from datetime import datetime
from alipay import AliPay
from alipay.utils import AliPayConfig
import os,json,random
from flask import current_app

@jsonrpc.method("Recharge.create")
@jwt_required #验证jwt
def create_recharge(money=10):
    """创建充值订单"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "error": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }
    order_number = datetime.now().strftime("%y%m%d%H%M%S") + "%08d" %user.id + "%04d" %random.randint(0,9999)
    print("************ 订单号为 *************")
    print(order_number)
    print("**********************************")

    recharge = Recharge(
        status = False,
        out_trade_number=order_number,
        name="账号充值-%s元" % money,
        user_id=user.id,
        money=money
    )
    db.session.add(recharge)
    db.session.commit()

    # 创建支付宝sdk对象
    app_private_key_string = open(os.path.join(current_app.BASE_DIR,"application/apps/users/keys/app_private_key.pem")).read()
    alipay_public_key_string = open(os.path.join(current_app.BASE_DIR, "application/apps/users/keys/alipay_public_key.pem")).read()

    alipay = AliPay(
        appid=current_app.config.get("ALIPAY_APP_ID"),
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type=current_app.config.get("ALIPAY_SIGN_TYPE"),
        debug=False,  # 默认False
        config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
    )

    order_string = alipay.api_alipay_trade_app_pay(
        out_trade_no=recharge.out_trade_number, # 订单号
        total_amount=float(recharge.money), # 订单金额
        subject=recharge.name, # 订单标题
        notify_url=current_app.config.get("ALIPAY_NOTIFY_URL") # 服务端的地址,自定义一个视图
    )
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "sandbox": current_app.config.get("ALIPAY_SANDBOX"),
        "order_string": order_string,
        "order_number": recharge.out_trade_number,
    }

from flask import request
def notify_response():
    """支付宝支付结果的异步通知处理"""
    data = request.form.to_dict()
    # sign 不能参与签名验证

    app_private_key_string = open(
        os.path.join(current_app.BASE_DIR, "application/apps/users/keys/app_private_key.pem")).read()
    alipay_public_key_string = open(
        os.path.join(current_app.BASE_DIR, "application/apps/users/keys/alipay_public_key.pem")).read()

    alipay = AliPay(
        appid=current_app.config.get("ALIPAY_APP_ID"),
        app_notify_url=None,  # 默认回调url
        app_private_key_string=app_private_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_string=alipay_public_key_string,
        sign_type=current_app.config.get("ALIPAY_SIGN_TYPE"),
        debug=False,  # 默认False
        config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
    )

    # verify
    success = alipay.verify(data, signature)
    if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
        """充值成功"""
        out_trade_number = data["out_trade_no"]
        recharge = Recharge.query.filter(Recharge.out_trade_number == out_trade_number).first()
        if recharge is None:
            return "fail"
        recharge.status = True
        user = User.query.get(recharge.user_id)
        if user is None:
            return "fail"
        user.money += recharge.money
        db.session.commit()
    return "success"  # 必须只能是success

@jsonrpc.method("Recharge.return")
@jwt_required # 验证jwt
def return_recharge(out_trade_number):
    """同步通知处理"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if user is None:
        return {
            "errno": status.CODE_NO_USER,
            "errmsg": message.user_not_exists,
        }

    recharge = Recharge.query.filter(Recharge.out_trade_number==out_trade_number).first()
    if recharge is None:
        return {
            "errno": status.CODE_RECHARGE_ERROR,
            "errmsg": message.recharge_not_exists,
        }

    recharge.status=True
    user.money+=recharge.money
    db.session.commit()
    return {
        "errno": status.CODE_OK,
        "errmsg": message.ok,
        "money": float( "%.2f" % user.money),
    }

def check_recharge():
    """可以使用查询订单借口保证支付结果同步处理的安全性"""
    # out_trade_numbe = "201229102634000000520662"
    # app_private_key_string = open(os.path.join(current_app.BASE_DIR, "application/apps/users/keys/app_private_key.pem")).read()
    # alipay_public_key_string = open(os.path.join(current_app.BASE_DIR, "application/apps/users/keys/app_public_key.pem")).read()
    #
    # alipay = AliPay(
    #     appid= current_app.config.get("ALIPAY_APP_ID"),
    #     app_notify_url=None,  # 默认回调url
    #     app_private_key_string=app_private_key_string,
    #     # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    #     alipay_public_key_string=alipay_public_key_string,
    #     sign_type=current_app.config.get("ALIPAY_SIGN_TYPE"),
    #     debug = False,  # 默认False
    #     config = AliPayConfig(timeout=15)  # 可选, 请求超时时间
    # )
    # result = alipay.api_alipay_fund_trans_order_query(
    #     order_id=out_trade_numbe
    # )
    # print(result)
    # return result
    return ""


