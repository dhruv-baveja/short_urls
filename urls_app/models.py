from __future__ import unicode_literals

from django.db import models


class UrlMap(models.Model):
    short_url = models.CharField(max_length=8, null=True)
    long_url = models.URLField(max_length=254)
    count = models.IntegerField()

    class Meta:
        db_table = 'url_map'
