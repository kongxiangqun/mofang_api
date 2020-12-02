from . import InitConfig


class Config(InitConfig):
    """项目开发环境配置"""
    DEBUG = True

    # 配置数据库连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql://mofang_user:mofang@127.0.0.1:3306/mofang?charset=utf8mb4'
    SQLALCHEMY_ECHO = True

    # Redis
    REDIS_URL = 'redis://@127.0.0.1:6379/0'

    # session存储配置
    SESSION_REDIS_HOST = '127.0.0.1'
    SESSION_REDIS_PORT = 6379
    SESSION_REDIS_DB = 1

    # 日志配置
    LOG_LEVEL        = "DEBUG"             # 日志输出到文件中的最低等级
    LOG_DIR          = "/logs/mofang.log"  # 日志存储目录
    LOG_MAX_BYTES    = 300 * 1024 * 1024   # 单个日志文件的存储上限[单位: b]
    LOG_BACKPU_COUNT = 20                  # 日志文件的最大备份数量
    LOG_NAME = "mofang"                    # 日志器名称

    # 短信相关配置
    SMS_ACCOUNT_ID = "8a216da8754a45d5017564dc514207fe"  # 接口主账号
    SMS_ACCOUNT_TOKEN = "759a69dae5134080b26cd1869069e410"  # 认证token令牌
    SMS_APP_ID = "8a216da8754a45d5017564dc52250804"  # 应用ID
    SMS_TEMPLATE_ID = 1  # 短信模板ID
    SMS_EXPIRE_TIME = 60 * 5  # 短信有效时间，单位:秒/s
    SMS_INTERVAL_TIME = 60  # 短信发送冷却时间，单位:秒/s


    import sys
    # import os
    #
    # BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # print("------ 添加环境变量 -------")
    # print(BASE_DIR)
    # print("-------------")
    # sys.path.insert(0,os.path.join(BASE_DIR, 'apps'))
    print(sys.path)
    # 蓝图注册列表
    INSTALLED_APPS = [
        'application.apps.home',
        'application.apps.users',
        'application.apps.marsh',
        # "home",
        # "users",
        # "marsh",
    ]
