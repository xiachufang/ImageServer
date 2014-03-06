import os


MODULE_NAME = os.path.dirname(os.path.abspath(__file__)).split('/')[-1]


class BaseConfig(object):
    pass


class ProductionConfig(BaseConfig):
    BEANSDBCFG = {
        'localhost:7901': range(16),
        'localhost:7902': range(16),
    }
    DEBUG = False
    REDIS_SERVER = 'redis://localhost/0'
    BAIDUYUN = {
        'ak': 'access token',
        'sk': 'secret token',
        'bucket': 'bucket',
    }
    IMAGE_QUALITY = 90
    IMAGE_KEY = '6d98a7186f1173b945add7f40cd28a85'


class DevelopmentConfig(BaseConfig):
    BEANSDBCFG = {
        'localhost:7901': range(16),
        'localhost:7902': range(16),
    }
    DEBUG = True
    REDIS_SERVER = 'redis://localhost/3'
    BAIDUYUN = {
        'ak': 'access token',
        'sk': 'secret token',
        'bucket': 'bucket',
    }
    IMAGE_QUALITY = 90
    IMAGE_KEY = '976da248917d92669d5eae619b2f43e7'


Config = DevelopmentConfig
