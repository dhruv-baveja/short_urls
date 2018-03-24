from rest_framework import serializers

from .utils import get_short_url
from .models import UrlMap


class LongUrlsSerializer(serializers.Serializer):
    long_urls = serializers.ListField(
        child=serializers.CharField(max_length=254)
    )

    def create(self, validated_data):
        urls_map_query = UrlMap.objects.filter(long_url__in=validated_data['long_urls'])
        existing_url_maps = urls_map_query.values_list('long_url', flat=True)

        for long_url in validated_data['long_urls']:
            if long_url in existing_url_maps:
                continue
            url_map, created = UrlMap.objects.get_or_create(
                long_url=long_url,
                defaults={'count': 0}
            )
            if created:
                short_url = get_short_url(url_map.id)
                url_map.short_url = short_url
                url_map.save()

        return urls_map_query


class ShortUrlsSerializer(serializers.Serializer):
    short_urls = serializers.ListField(
        child=serializers.CharField(max_length=8)
    )


class UrlMapSerializer(serializers.Serializer):
    long_url = serializers.URLField(max_length=254)
    short_url = serializers.CharField(max_length=8)
    count = serializers.IntegerField()

