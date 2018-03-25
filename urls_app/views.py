import re

from django.shortcuts import redirect
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from .serializers import (
    LongUrlsSerializer, ShortUrlsSerializer
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
                data = serializer.save()
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
                data = url_maps
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
        mongo_db = settings.PRIMARY_DATABASE
        short_urls = list(set(short_urls))
        existing_short_urls = list(mongo_db.url_map.find(
            {"short_url": {"$in": short_urls}},
            projection={'_id': False}
        ))
        if len(short_urls) > len(existing_short_urls):
            is_valid = False
            existing_short_urls_list = [item['short_url'] for item in existing_short_urls]

            for item in short_urls:
                if item not in existing_short_urls_list:
                    errors.append(item)

        return is_valid, errors, existing_short_urls


@api_view(['GET'])
def short_url_redirect(request, short_url):
    mongo_db = settings.PRIMARY_DATABASE
    short_url_obj = mongo_db.url_map.find_one({'short_url': short_url})
    if short_url_obj:
        mongo_db.url_map.update({'short_url': short_url}, {'$inc': {'count': 1}})
        return redirect(short_url_obj['long_url'])
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)
