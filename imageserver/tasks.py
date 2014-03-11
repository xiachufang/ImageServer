from urllib import unquote
from celery.task.http import URL
from .init import celery, beans, bdyun


@celery.task
def async_upload_to_bdyun(ident, sizes=[], callback=''):
    for w, h in sizes:
        im = beans.get_image(ident, w)
        path = bdyun_path(ident, w, h)
        ret = bdyun.put_object(path, im.to_string())
        if not ret:
            print 'Sync pic', path, 'failed!'
            return

    if callback:
        URL(unquote(callback)).post_async(
            ident=ident,
            sizes=sizes,
        )


def bdyun_path(ident, width=None, height=None):
    if width:
        return '/image/{}/{}.jpg'.format(width, ident)

    return '/image/{}.jpg'.format(ident)
