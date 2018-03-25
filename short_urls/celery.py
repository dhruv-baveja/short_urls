from __future__ import absolute_import, unicode_literals
import os
from datetime import timedelta

from django.conf import settings
from celery import Celery
from kombu import Exchange, Queue

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj.settings')

app = Celery('short_urls')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.update(
    CELERY_DEFAULT_QUEUE='short_urls',
    CELERY_QUEUES=(
        Queue('short_urls', Exchange('short_urls'), routing_key='short_urls'),
    ),
    CELERYBEAT_SCHEDULE={
        'short_url_pool_refill': {
            'task': 'urls_app.tasks.check_and_update_pool',
            'schedule': timedelta(seconds=7200)
        }
    },
    CELERY_TIMEZONE='UTC'
)
