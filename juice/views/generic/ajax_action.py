# -*- coding: utf-8 -*-
from types import MethodType

from django.views.generic import View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.utils import six


class ParamExtractionError(Exception):
    pass


class AjaxActionView(View):
    """

    """

    http_method_names = ['post']
    post_parameters = []

    # TODO custom hanlers

    def __init__(self, *args, **kwargs):
        super(AjaxActionView, self).__init__(*args, **kwargs)

        def get_handler(param_name, param_type):
            attr_name = '_'+param_name

            def str_handler(self, request):
                if param_name not in request.POST:
                    raise ParamExtractionError
                setattr(self, attr_name, request.POST[param_name])

            def int_handler(self, request):
                try:
                    setattr(self,
                            attr_name,
                            int(request.POST.get(param_name, None)))
                except (TypeError, ValueError):
                    raise ParamExtractionError

            def bool_handler(self, request):
                value = request.POST.get(param_name, None)
                if value is None or value.lower() not in ['true', 'false']:
                    raise ParamExtractionError
                setattr(self, attr_name, value.lower() == 'true')

            return locals()[param_type + '_handler']

        norm_post_parameters = []
        for x in self.post_parameters:

            if isinstance(x, six.string_types):
                param_name, param_type = x, 'str'
            else:
                param_name, param_type = x

            if param_type in ['str', 'int', 'bool']:
                handler = MethodType(
                    get_handler(param_name, param_type), self)
            elif param_type == 'custom':
                print '2'
                handler = getattr(self, "_handle_"+param_name)
            else:
                msg = "Unknown param type '{0}'".format(param_type)
                raise ImproperlyConfigured(msg)

            norm_post_parameters.append((x, handler))
        self.post_parameters = norm_post_parameters

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("Not Ajax request.")

        try:
            for x, handler in self.post_parameters:
                handler(request)
        except ParamExtractionError:
            return HttpResponseBadRequest()

        return self.action(request)
