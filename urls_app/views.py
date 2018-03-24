import re

from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .models import UrlMap
from .serializers import (
    LongUrlsSerializer, UrlMapSerializer, ShortUrlsSerializer
)


class LongUrls(APIView):

    def post(self, request):
        data = request.data
        serializer = LongUrlsSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            is_valid, errors = self._validate_long_urls(serializer.data['long_urls'])

            data = []
            status_codes = ['INVALID_URLS']
            state = 'FAILED'
            response_status = status.HTTP_400_BAD_REQUEST
            if is_valid:
                url_maps = serializer.save()
                data = UrlMapSerializer(instance=url_maps, many=True).data
                status_codes = []
                state = 'OK'
                response_status = status.HTTP_200_OK

            output = {
                'data': data,
                'invalid_urls': errors,
                'status_codes': status_codes,
                'status': state
            }
            return Response(
                output,
                status=response_status
            )

    @staticmethod
    def _validate_long_urls(long_urls):
        errors = []
        is_valid = True
        regex = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        for long_url in long_urls:
            if not re.fullmatch(regex, long_url):
                is_valid = False
                errors.append(long_url)

        return is_valid, errors


class ShortUrls(APIView):

    def post(self, request):
        data = request.data
        serializer = ShortUrlsSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            is_valid, errors, url_maps = self._validate_and_get_short_urls(serializer.data['short_urls'])
            data = []
            status_codes = ['SHORT_URLS_NOT_FOUND']
            state = 'FAILED'
            response_status = status.HTTP_400_BAD_REQUEST
            if is_valid:
                data = UrlMapSerializer(instance=url_maps, many=True).data
                status_codes = []
                state = 'OK'
                response_status = status.HTTP_200_OK

            output = {
                'data': data,
                'invalid_urls': errors,
                'status_codes': status_codes,
                'status': state
            }
            return Response(
                output,
                status=response_status
            )

    @staticmethod
    def _validate_and_get_short_urls(short_urls):
        errors = []
        is_valid = True
        data = []

        short_urls_query = UrlMap.objects.filter(short_url__in=short_urls)
        existing_short_urls = short_urls_query.values_list('short_url', flat=True)
        if len(short_urls) > short_urls_query.count():
            is_valid = False

        for short_url in short_urls:
            if short_url not in existing_short_urls:
                errors.append(short_url)

        if is_valid:
            data = short_urls_query

        return is_valid, errors, data


@api_view(['GET'])
def short_url_redirect(request, short_url):

    try:
        url_map = UrlMap.objects.get(short_url=short_url)
    except UrlMap.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        url_map.count += 1
        url_map.save()
        return redirect(url_map.long_url)
