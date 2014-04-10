#coding: utf8
from flask import Flask
from .config import MODULE_NAME
from .lib.dbclient import Beansdb
from .lib.storage import BeansStorage
from .init_celery import celery  # noqa


app = Flask(__name__)
app.config.from_object('%s.config.Config' % MODULE_NAME)

beans_conn = Beansdb(app.config['BEANSDBCFG'], 16)
beans = BeansStorage(beans_conn, app.config['HEIGHT_IN_IDENT'], logger=app.logger, quality=app.config['IMAGE_QUALITY'])
