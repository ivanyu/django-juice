from django.http import HttpResponse
from django.utils import simplejson


class JsonResponse(HttpResponse):
    def __init__(self, dictionary):
        super(JsonResponse, self).__init__(
            simplejson.dumps(dictionary),
            content_type='application/json')
