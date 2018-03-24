from unittest import mock

from rest_framework.test import APITestCase, APIRequestFactory
from model_mommy import mommy

from ..views import LongUrls, ShortUrls, short_url_redirect
from ..models import UrlMap


class LongUrlsTest(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

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
        for item in request_data["long_urls"]:
            self.assertIsInstance(UrlMap.objects.get(long_url=item), UrlMap)

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
        for item in request_data["long_urls"]:
            self.assertTrue(item in response.data["invalid_urls"])

    def test_validate_long_urls(self):
        long_urls = [
            "https://www.hackerearth.com/challenge/hiring/hackerearth-python-developer-hiring-challenge/",
            "www.google.com"
        ]

        output = LongUrls._validate_long_urls(long_urls)
        self.assertEqual(output, (False, ['www.google.com']))


class ShortUrlsTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.url_map_1 = mommy.make(
            UrlMap,
            long_url="https://www.hackerearth.com/challenge/hiring/hackerearth-python-developer-hiring-challenge/",
            short_url=1,
            count=0
        )
        self.url_map_2 = mommy.make(
            UrlMap,
            long_url="https://www.hackerearth.com/",
            short_url=2,
            count=0
        )

    def test_post_valid_data(self):
        request_data = {
            "short_urls": [
                "1",
                "2"
            ]
        }
        request = self.factory.post(
            '/short_urls/', request_data, format='json'
        )
        view = ShortUrls.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 2)
        for item in response.data["data"]:
            if item["short_url"] == '1':
                self.assertEqual(self.url_map_1.long_url, item["long_url"])
            else:
                self.assertEqual(self.url_map_2.long_url, item["long_url"])

    def test_post_invalid_data(self):
        request_data = {
            "short_urls": [
                "1",
                "3"
            ]
        }
        request = self.factory.post(
            '/short_urls/', request_data, format='json'
        )
        view = ShortUrls.as_view()
        response = view(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['invalid_urls'], ['3'])


class ShortUrlRedirectTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.url_map_1 = mommy.make(
            UrlMap,
            long_url="https://www.hackerearth.com/challenge/hiring/hackerearth-python-developer-hiring-challenge/",
            short_url=1,
            count=0
        )
        self.url_map_2 = mommy.make(
            UrlMap,
            long_url="https://www.hackerearth.com/",
            short_url=2,
            count=0
        )

    @mock.patch('urls_app.views.redirect')
    def test_invalid_short_url(self, redirect_mock):
        request = self.factory.get('/3/')
        response = short_url_redirect(request, '3')
        self.assertEqual(response.status_code, 404)

    @mock.patch('urls_app.views.redirect')
    def test_valid_short_url(self, redirect_mock):
        request = self.factory.get('/2/')
        
        response = short_url_redirect(request, '2')

