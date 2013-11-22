#coding: utf8
from flask import Flask
from celery import Celery
from .config import MODULE_NAME
from .lib.dbclient import Beansdb
from .lib.storage import BeansStorage
from .lib.bdyun import BaiduYun


app = Flask(__name__)
app.config.from_object('%s.config.DevelopmentConfig' % MODULE_NAME)
# app.config.from_object('%s.config.ProductionConfig' % MODULE_NAME)

beans_conn = Beansdb(app.config['BEANSDBCFG'], 16)
beans = BeansStorage(beans_conn, app.config['HEIGHT_IN_IDENT'], logger=app.logger)

bdyun = BaiduYun(
    ak=app.config['BAIDUYUN']['ak'],
    sk=app.config['BAIDUYUN']['sk'],
    bucket=app.config['BAIDUYUN']['bucket'],
)

celery = Celery(
    'celery',
    broker=app.config['REDIS_SERVER'],
    include=(
        '%s.tasks' % MODULE_NAME,
        'celery.task.http',
    ),
)

celery.conf.update(
    CELERY_IGNORE_RESULT=True,
    CELERY_DISABLE_RATE_LIMITS=True,
)
