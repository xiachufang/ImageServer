import os


MODULE_NAME = os.path.dirname(os.path.abspath(__file__)).split('/')[-1]


class BaseConfig(object):
    HEIGHT_IN_IDENT = False


class ProductionConfig(BaseConfig):
    BEANSDBCFG = {
        'carrot:7901': range(16),
        'onion:7902': range(16),
    }
    DEBUG = False
    REDIS_SERVER = 'redis://localhost/0'
    BAIDUYUN = {
        'ak': '6bd064731412b390b865efe5ca25f602',
        'sk': '8c36eb983b391b2a320ef782fbc192a3',
        'bucket': 'xcfimg',
    }


class DevelopmentConfig(BaseConfig):
    BEANSDBCFG = {
        'localhost:7901': range(16),
        'localhost:7902': range(16),
    }
    DEBUG = True
    REDIS_SERVER = 'redis://localhost/3'
    BAIDUYUN = {
        'ak': '6bd064731412b390b865efe5ca25f602',
        'sk': '8c36eb983b391b2a320ef782fbc192a3',
        'bucket': 'xcfimg',
    }
