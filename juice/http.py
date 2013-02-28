from django.http import HttpResponse
from django.utils import simplejson


class JsonResponse(HttpResponse):
    def __init__(self, dictionary):
        content = simplejson.dumps(dictionary)
        super(JsonResponse, self).__init__(
            content, content_type='application/json')
