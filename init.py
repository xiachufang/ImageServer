#coding: utf8
from flask import Flask
from dbclient import Beansdb
from storage import BeansStorage


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
# app.config.from_object('config.ProductionConfig')

beans_conn = Beansdb(app.config['BEANSDBCFG'], 16)
beans = BeansStorage(beans_conn, app.config['HEIGHT_IN_IDENT'], logger=app.logger)
