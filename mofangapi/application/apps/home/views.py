# from application import jsonrpc
#
#
# @jsonrpc.method(name='Home.index')
# def home(id):
#     return "hello world! id=%s" % id

# 短信公共业务
from application import jsonrpc
import re,random,json
from status import APIStatus as status
from message import ErrorMessage as message
from ronglian_sms_sdk import SmsSDK
from flask import current_app
from application import redis
@jsonrpc.method(name="Home.sms")
def sms(mobile):
    """发送短信验证码"""
    # 验证手机
    if not re.match("^1[3-9]\d{9}$",mobile):
        return {"errno": status.CODE_VALIDATE_ERROR, "errmsg": message.mobile_format_error}

    # 短信发送冷却时间
    ret = redis.get("int_%s" % mobile)
    if ret is not None:
        return {"errno": status.CODE_INTERVAL_TIME, "errmsg": message.sms_interval_time}

    # 生成验证码
    sms_code = "%06d" % random.randint(0,999999)
    # 发送短信
    sdk = SmsSDK(
        current_app.config.get("SMS_ACCOUNT_ID"),
        current_app.config.get("SMS_ACCOUNT_TOKEN"),
        current_app.config.get("SMS_APP_ID")
    )
    ret = sdk.sendMessage(
        current_app.config.get("SMS_TEMPLATE_ID"),
        mobile,
        (sms_code, current_app.config.get("SMS_EXPIRE_TIME") // 60)
    )
    result = json.loads(ret)
    if result["statusCode"] == "000000":
        pipe = redis.pipeline()
        pipe.multi()  # 开启事务
        # 保存短信记录到redis中
        pipe.setex("sms_%s" % mobile,current_app.config.get("SMS_EXPIRE_TIME"),sms_code)
        # 进行冷却倒计时
        pipe.setex("int_%s" % mobile,current_app.config.get("SMS_INTERVAL_TIME"),"_")
        pipe.execute() # 提交事务
        # 返回结果
        return {"errno":status.CODE_OK, "errmsg": message.ok}
    else:
        return {"errno": status.CODE_SMS_ERROR, "errmsg": message.sms_send_error}

