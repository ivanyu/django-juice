# -*- coding: utf-8 -*-
from types import MethodType

from django.views.generic import View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.utils import six


class AjaxActionView(View):
    """

    """
    
    class __ParamExtractionError(Exception):
        pass

    http_method_names = ['post']
    post_parameters = []

    # TODO custom hanlers

    def __init__(self, *args, **kwargs):
        super(AjaxActionView, self).__init__(*args, **kwargs)

        def get_handler(param_name, param_type):
            attr_name = '_'+param_name

            def srt_handler(self, request):
                if param_name not in request.POST:
                    raise self.__ParamExtractionError
                setattr(self, attr_name, request.POST[param_name])

            def int_handler(self, request):
                try:
                    setattr(self,
                            attr_name,
                            int(request.POST.get(param_name, None)))
                except (TypeError, ValueError):
                    raise self.__ParamExtractionError

            def bool_handler(self, request):
                value = request.POST.get(param_name, None)
                if value is None or value.lower() not in ['true', 'false']:
                    raise self.__ParamExtractionError
                setattr(self, attr_name, value.lower() == 'true')

            return locals()[param_type + '_handler']

        norm_post_parameters = []
        for x in self.post_parameters:
            if isinstance(x, six.string_types):
                handler = MethodType(get_handler(x, 'str'), self)
            else:
                param_name, param_type = x
                if param_type not in ['str', 'int', 'bool']:
                    msg = "Unknown param type '{0}'".format(param_type)
                    raise ImproperlyConfigured(msg)
                handler = MethodType(get_handler(param_name, param_type), self)
            norm_post_parameters.append((x, handler))
        self.post_parameters = norm_post_parameters

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("Not Ajax request.")

        for x, handler in self.post_parameters:
            handler(request)

        return self.action(request)
