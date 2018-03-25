import hashlib
import string
import random

import arrow
import pymongo
from django.conf import settings
from pymongo.errors import DuplicateKeyError


def get_short_urls(count):
    mongo_db = settings.PRIMARY_DATABASE
    short_urls = []
    for _ in range(count):
        short_urls.append(mongo_db.short_urls_pool.find_one_and_delete(
            {'used': 1}, projection={'_id': False, 'used': False},
            sort=[('_id', pymongo.DESCENDING)]
        )['short_url'])

    return short_urls


def generate_short_urls(count):
    for i in range(count):
        create_short_url_string()


def create_short_url_string(length=settings.SHORT_URL_LENGTH):
    chars = string.ascii_letters + string.digits
    mongo_db = settings.PRIMARY_DATABASE
    short_url = ''.join(random.choice(chars) for _ in range(length))

    try:
        mongo_db.short_urls_pool.insert({"short_url": short_url, "used": 1})
        return
    except DuplicateKeyError:
        create_short_url_string()
