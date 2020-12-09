class APIStatus():
    CODE_OK = 1000 # 接口操作成功
    CODE_VALIDATE_ERROR = 1001 # 验证有误!

    CODE_SMS_ERROR = 1002  # 短信功能执行失败
    CODE_INTERVAL_TIME = 1003  # 短信发送冷却中

    CODE_NO_AUTHORIZATION = 1004  # 请求中没有附带认证信息
    CODE_SIGNATURE_EXPIRED = 1005  # 请求中的认证信息已过期
    CODE_INVALID_AUTHORIZATION = 1006  # 请求中的认证信息无效

    CODE_NO_ACCOUNT = 1007  # 请求中没有账户信息
    CODE_NO_USER = 1008  # 用户不存在
    CODE_PASSWORD_ERROR = 1009  # 密码错误

    CODE_CAPTCHA_ERROR = 1010  # 验证码验证失败
