from importlib import import_module


def load_config(config_path):
    """自动加载配置"""
    module = import_module(config_path)
    # application.settings.dev
    # -1就是 dev
    name = config_path.split('.')[-1]
    if name == 'settings':
        # 既不是dev也不是prod 就返回InitConfig
        return module.InitConfig
    else:
        # 返回各自的Config
        return module.Config
