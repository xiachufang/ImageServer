from celery import Celery
from functions import optimize_pic as _optimize_pic


BROKER_URL = 'redis://localhost/0'
celery = Celery(
    'celery',
    broker=BROKER_URL,
)

celery.conf.update(
    CELERY_IGNORE_RESULT=True,
    CELERY_DISABLE_RATE_LIMITS=True,
)


@celery.task
def optimize_pic(picpath):
    _optimize_pic(picpath)
