from celery import Celery
from .config import MODULE_NAME, Config


celery = Celery(
    'celery',
    broker=Config.REDIS_SERVER,
    include=(
        '%s.tasks' % MODULE_NAME,
        'celery.task.http',
    ),
)

celery.conf.update(
    CELERY_IGNORE_RESULT=True,
    CELERY_DISABLE_RATE_LIMITS=True,
    CELERY_ACKS_LATE=True,
    CELERY_ACCEPT_CONTENT=['pickle', 'json'],
)
