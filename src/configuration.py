import json
from os.path import dirname, join, exists
from datetime import datetime
class ConfigurationFactory:

    @staticmethod
    def create_btest_config():
        _root_dir = dirname(dirname(__file__))
        _conf_path = join(_root_dir, "conf", "backtest_config.json")
        if exists(_conf_path):
            try:
                with open(_conf_path) as _conf:
                    conf = json.load(_conf)
                    print("{} - Successfully loaded configuration file".format(datetime.now()))
                    return conf
            except Exception as e:
                print(str(e))
        else:
            print("Error loading backtest configuration please check /conf directory")

