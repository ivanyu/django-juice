# -*- coding: utf-8 -*-
"""
HTTP utilities.

`JsonResponse` - a subclass of `HttpResponse` which converts dictionary passed
to its constructor to JSON format and sets ContentType header to
"application/json".
"""

from django.http import HttpResponse
from django.utils import simplejson


class JsonResponse(HttpResponse):
    """
    A subclass of `HttpResponse` which converts dictionary passed to its
    constructor to JSON format and sets ContentType header to
    "application/json".
    """

    def __init__(self, dictionary):
        super(JsonResponse, self).__init__(
            simplejson.dumps(dictionary),
            content_type='application/json')
