import os


MODULE_NAME = os.path.dirname(os.path.abspath(__file__)).split('/')[-1]


class BaseConfig(object):
    HEIGHT_IN_IDENT = False


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


class DevelopmentConfig(BaseConfig):
    BEANSDBCFG = {
        'localhost:7901': range(16),
        'localhost:7902': range(16),
    }
    DEBUG = True
    REDIS_SERVER = 'redis://localhost/0'
    BAIDUYUN = {
        'ak': 'access token',
        'sk': 'secret token',
        'bucket': 'bucket',
    }
