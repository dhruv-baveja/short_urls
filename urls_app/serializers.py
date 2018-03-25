from rest_framework import serializers
from django.conf import settings
from django.core.cache import cache

from .utils import get_short_urls


class LongUrlsSerializer(serializers.Serializer):
    long_urls = serializers.ListField(
        child=serializers.CharField(max_length=254)
    )

    def create(self, validated_data):
        long_urls = set(validated_data['long_urls'])
        url_maps = []
        cached_long_urls = self._get_cached_long_urls(long_urls)
        new_long_urls = list(long_urls - set(cached_long_urls))
        new_short_urls = get_short_urls(len(new_long_urls))
        new_insertion_list = []
        response_list = []
        for i in range(len(new_long_urls)):
            new_insertion_list.append(
                {
                    'short_url': new_short_urls[i],
                    'long_url': new_long_urls[i],
                    'count': 0
                }
            )
            cache.set(new_long_urls[i], new_short_urls[i], settings.LONG_URL_CACHE_TIMEOUT)
            response_list.append(
                {
                    'short_url': new_short_urls[i],
                    'long_url': new_long_urls[i]
                }
            )
        if cached_long_urls:
            for long, short in cached_long_urls.items():
                response_list.append(
                    {
                        'short_url': short,
                        'long_url': long
                    }
                )

        if new_insertion_list:
            mongo_db = settings.PRIMARY_DATABASE
            mongo_db.url_map.insert_many(new_insertion_list)

        return response_list

    def _get_cached_long_urls(self, long_urls):
        return cache.get_many(long_urls)


class ShortUrlsSerializer(serializers.Serializer):
    short_urls = serializers.ListField(
        child=serializers.CharField(max_length=8)
    )
