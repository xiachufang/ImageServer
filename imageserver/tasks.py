import sys
import qiniu.conf
import qiniu.rs
import qiniu.io
from urllib import unquote
from celery.task.http import URL
from .init import celery, beans
from config import Config


qiniu.conf.ACCESS_KEY = Config.QINIUCFG['access_key']
qiniu.conf.SECRET_KEY = Config.QINIUCFG['secret_key']


@celery.task
def async_upload_to_cloud(ident, sizes=[], callback=''):
    for w, h in sizes:
        im = beans.get_image(ident, w, h)
        path = qiniu_path(ident, w, h)
        upload_to_qiniu(path, im.to_string())

    feedback(callback, ident, sizes)


def upload_to_qiniu(path, data):
    policy = qiniu.rs.PutPolicy(Config.QINIUCFG['bucket'])
    uptoken = policy.token()
    ret, err = qiniu.io.put(uptoken, path, data)
    if err is not None:
        sys.stderr.write('error: %s\n' % err)
        return


def qiniu_path(ident, width=None, height=None):
    if width:
        return 'image/{}/{}.jpg'.format(width, ident)

    return 'image/{}.jpg'.format(ident)


def feedback(callback, ident, sizes):
    if callback:
        URL(unquote(callback)).post_async(
            ident=ident,
            sizes=sizes,
        )
