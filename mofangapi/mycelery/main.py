# 加入绝对引入这个新特性
from __future__ import absolute_import
from celery import Celery
from application import init_app

# 初始化celery对象
app = Celery("flask")

# 初始化flask对象
flask_app = init_app("application.settings.dev").app

# 加载配置
app.config_from_object("mycelery.config")

# 自动注册任务
app.autodiscover_tasks(["mycelery.sms"])



