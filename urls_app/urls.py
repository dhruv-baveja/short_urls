from django.conf.urls import url

from .views import LongUrls, ShortUrls, short_url_redirect


urlpatterns = [
    url(r'^urls/long/', LongUrls.as_view()),
    url(r'^urls/short/', ShortUrls.as_view()),
    url(r'^(?P<short_url>[\w]+)/$', short_url_redirect),
]
