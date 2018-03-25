from unittest import mock

import redis
from django.conf import settings
from django.test import override_settings
from rest_framework.test import APITestCase, APIRequestFactory
from model_mommy import mommy

from ..views import LongUrls, ShortUrls, short_url_redirect
from ..models import UrlMap


@override_settings(REDIS_CON=redis.Redis(host='localhost', port=6379, db=1))
class LongUrlsTest(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.r_con = settings.REDIS_CON

    def test_post_valid_data(self):
        request_data = {
            "long_urls": [
                "https://www.hackerearth.com/challenge/hiring/hackerearth-python-developer-hiring-challenge/",
                "http://www.google.com"
            ]
        }
        request = self.factory.post(
            '/long_urls/', request_data, format='json'
        )
        view = LongUrls.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 2)

        for item in response.data["data"]:
            if item['long_url'] == request_data['long_urls'][0]:
                self.assertEqual(self.r_con.get(item['short_url']).decode('utf-8'), item['long_url'])
            else:
                self.assertEqual(self.r_con.get(item['short_url']).decode('utf-8'), item['long_url'])

    def test_post_invalid_data(self):
        request_data = {
            "long_urls": [
                "www.hackerearth.com/challenge/hiring/hackerearth-python-developer-hiring-challenge/",
                "google.com"
            ]
        }
        request = self.factory.post(
            '/long_urls/', request_data, format='json'
        )

        view = LongUrls.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(response.data['data']), 0)
        for item in request_data["long_urls"]:
            self.assertTrue(item in response.data["invalid_urls"])

    def test_validate_long_urls(self):
        long_urls = [
            "https://www.hackerearth.com/challenge/hiring/hackerearth-python-developer-hiring-challenge/",
            "www.google.com"
        ]

        output = LongUrls._validate_long_urls(long_urls)
        self.assertEqual(output, (False, ['www.google.com']))


@override_settings(REDIS_CON=redis.Redis(host='localhost', port=6379, db=1))
class ShortUrlsTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.r_con = settings.REDIS_CON

        self.r_con.set('2wnf45h9', 'http://www.google.com')
        self.r_con.set('1kng74hl', 'https://www.google.com')
        self.r_con.set('2wnf45h9:count', 1)
        self.r_con.set('1kng74hl:count', 3)

    def test_post_valid_data(self):
        request_data = {
            'short_urls': [
                '2wnf45h9',
                '1kng74hl'
            ]
        }
        request = self.factory.post(
            '/short_urls/', request_data, format='json'
        )
        view = ShortUrls.as_view()
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 2)

        for item in response.data['data']:
            if item['short_url'] == '2wnf45h9':
                self.assertEqual('http://www.google.com', item['long_url'])
                self.assertEqual('1', item['count'])
            else:
                self.assertEqual('https://www.google.com', item['long_url'])
                self.assertEqual('3', item['count'])

    def test_post_invalid_data(self):
        request_data = {
            'short_urls': [
                '2wnf45h9',
                '8fj36dfh'
            ]
        }
        request = self.factory.post(
            '/short_urls/', request_data, format='json'
        )
        view = ShortUrls.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['invalid_urls'], ['8fj36dfh'])


@override_settings(REDIS_CON=redis.Redis(host='localhost', port=6379, db=1))
class ShortUrlRedirectTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.r_con = settings.REDIS_CON

        self.r_con.set('2wnf45h9', 'http://www.google.com')
        self.r_con.set('1kng74hl', 'https://www.google.com')

    def test_valid_short_url(self):
        request = self.factory.get('/2wnf45h9/')
        response = short_url_redirect(request, '2wnf45h9')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, 'http://www.google.com')

    def test_invalid_short_url(self):
        request = self.factory.get('/djd628dj/')
        response = short_url_redirect(request, 'djd628dj')
        self.assertEqual(response.status_code, 404)

