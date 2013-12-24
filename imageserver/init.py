#coding: utf8
from flask import Flask
from .config import MODULE_NAME
from .lib.dbclient import Beansdb
from .lib.storage import BeansStorage
from .lib.bdyun import BaiduYun
from .celery import celery  # noqa


app = Flask(__name__)
app.config.from_object('%s.config.Config' % MODULE_NAME)

beans_conn = Beansdb(app.config['BEANSDBCFG'], 16)
beans = BeansStorage(beans_conn, app.config['HEIGHT_IN_IDENT'], logger=app.logger)

bdyun = BaiduYun(
    ak=app.config['BAIDUYUN']['ak'],
    sk=app.config['BAIDUYUN']['sk'],
    bucket=app.config['BAIDUYUN']['bucket'],
)
