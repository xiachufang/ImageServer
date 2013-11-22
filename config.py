
class BaseConfig(object):
    HEIGHT_IN_IDENT = False


class ProductionConfig(BaseConfig):
    BEANSDBCFG = {
        "carrot:7901": range(16),
        "onion:7902": range(16),
    }
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    BEANSDBCFG = {
        "localhost:7901": range(16),
        "localhost:7902": range(16),
    }
    DEBUG = True
