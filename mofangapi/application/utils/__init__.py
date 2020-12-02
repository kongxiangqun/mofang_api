from flask import Blueprint
from importlib import import_module


def path(rule, func_view):
    # 把蓝图下视图和路由之间的映射关系处理成字典结构,方便后面注册蓝图的时候直接传参
    return {'rule': rule, 'view_func': func_view}


def include(url_prefix, blueprint_path):
    '''把路由前缀和蓝图做关系绑定'''
    return {'url_prefix': url_prefix, 'blueprint_path': blueprint_path}


def init_blueprint(app):
    """自动注册蓝图"""
    blueprint_path_list = app.config.get('INSTALLED_APPS')
    for blueprint_path in blueprint_path_list:
        blueprint_name = blueprint_path.split('.')[-1]
        # 自动创建蓝图对象
        blueprint = Blueprint(blueprint_name, blueprint_path)
        # 蓝图自动注册和绑定视图和子路由
        urls_module = import_module(blueprint_path + '.urls')  # 加载蓝图下的子路由文件
        print("********")
        print("urls_module", urls_module)
        print("urls_module.urlpatterns",urls_module.urlpatterns)
        print("********")
        for url in urls_module.urlpatterns:  # 遍历子路由中的所有路由
            blueprint.add_url_rule(**url)  # 将url注册到蓝图下

        # 读取总路由文件
        url_path = app.config.get('URL_PATH')
        urlpatterns = import_module(url_path).urlpatterns  # 加载蓝图下的子路由文件
        url_prefix = ''  # 蓝图路由前缀
        for urlpattern in urlpatterns:
            if urlpattern['blueprint_path'] == blueprint_name + '.urls':
                url_prefix = urlpattern['url_prefix']
                break

        # 注册模型
        import_module(blueprint_path + '.models')

        # 注册蓝图对象到app应用对象中
        app.register_blueprint(blueprint, url_prefix=url_prefix)
