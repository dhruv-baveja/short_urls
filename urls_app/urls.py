from django.conf.urls import url

from .views import LongUrls, ShortUrls, short_url_redirect


urlpatterns = [
    url(r'^long_urls/', LongUrls.as_view()),
    url(r'^short_urls/', ShortUrls.as_view()),
    url(r'^(?P<short_url>[\w]+)/$', short_url_redirect),
]
