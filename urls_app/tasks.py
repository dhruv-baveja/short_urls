from django.conf import settings
from celery import shared_task

from .utils import generate_short_urls


@shared_task
def check_and_update_pool():
    mongo_db = settings.PRIMARY_DATABASE
    if mongo_db.short_urls_pool.count() <= settings.SHORT_URL_BUFFER_SIZE:
        generate_short_urls(settings.SHORT_URL_REFILL_COUNT)
