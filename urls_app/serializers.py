from rest_framework import serializers
from django.db.utils import IntegrityError

from .utils import get_short_url
from .models import UrlMap


class LongUrlsSerializer(serializers.Serializer):
    long_urls = serializers.ListField(
        child=serializers.CharField(max_length=254)
    )

    def create(self, validated_data):
        url_maps = []
        for long_url in validated_data['long_urls']:
            url_map = self.generate_and_save(long_url)
            url_maps.append(url_map)

        return url_maps

    def generate_and_save(self, long_url):
        short_url = get_short_url(long_url)
        try:
            url_map = UrlMap.objects.create(
                long_url=long_url,
                short_url=short_url,
                count=0
            )
        except IntegrityError:
            self.generate_and_save(long_url)
        else:
            return url_map


class ShortUrlsSerializer(serializers.Serializer):
    short_urls = serializers.ListField(
        child=serializers.CharField(max_length=8)
    )


class UrlMapSerializer(serializers.Serializer):
    long_url = serializers.URLField(max_length=254)
    short_url = serializers.CharField(max_length=8)
    count = serializers.IntegerField()

