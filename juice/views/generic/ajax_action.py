# -*- coding: utf-8 -*-
from types import MethodType

from django.views.generic import View
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseBadRequest
from django.utils import six


class ParamExtractionError(Exception):
    pass


class RequestParamsExtractingMixin(object):
    def __init__(self, *args, **kwargs):
        super(RequestParamsExtractingMixin, self).__init__(*args, **kwargs)

        if not 'method' in kwargs:
            raise ImproperlyConfigured(
                "Keyword argument 'method' is required "
                "with possible values 'post' or 'get'.")
        self.method = kwargs['method']
        if self.method not in ['post', 'get']:
            raise ImproperlyConfigured(
                "Allowed values for 'method' are 'post' and 'get'.")

        def get_handler(param_name, param_type):
            attr_name = '_'+param_name

            def str_handler(self, request):
                params = getattr(request, self.method.upper())
                if param_name not in params:
                    raise ParamExtractionError
                setattr(self, attr_name, request.POST[param_name])

            def int_handler(self, request):
                params = getattr(request, self.method.upper())
                try:
                    setattr(self,
                            attr_name,
                            int(params.get(param_name, None)))
                except (TypeError, ValueError):
                    raise ParamExtractionError

            def bool_handler(self, request):
                params = getattr(request, self.method.upper())
                value = params.get(param_name, None)
                if value is None or value.lower() not in ['true', 'false']:
                    raise ParamExtractionError
                setattr(self, attr_name, value.lower() == 'true')

            return locals()[param_type + '_handler']

        norm_parameters = []
        for x in self._get_param_dict():

            if isinstance(x, six.string_types):
                param_name, param_type = x, 'str'
            else:
                param_name, param_type = x

            if param_type in ['str', 'int', 'bool']:
                handler = MethodType(
                    get_handler(param_name, param_type), self)
            elif param_type == 'custom':
                handler = getattr(self, "_handle_"+param_name)
            else:
                msg = "Unknown param type '{0}'".format(param_type)
                raise ImproperlyConfigured(msg)

            norm_parameters.append((x, handler))
        setattr(self, self._get_param_dict_name(), norm_parameters)

    def _get_param_dict_name(self):
        return self.method + '_parameters'

    def _get_param_dict(self):
        return getattr(self, self._get_param_dict_name())

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == self.method:
            try:
                for x, handler in self._get_param_dict():
                    handler(request)
            except ParamExtractionError:
                return HttpResponseBadRequest()
        return super(RequestParamsExtractingMixin, self).dispatch(
            request, *args, **kwargs)


class PostParamsExtractingMixin(RequestParamsExtractingMixin):
    post_parameters = []

    def __init__(self, *args, **kwargs):
        kwargs['method'] = 'post'
        super(PostParamsExtractingMixin, self).__init__(*args, **kwargs)


class GetParamsExtractingMixin(RequestParamsExtractingMixin):
    get_parameters = []

    def __init__(self, *args, **kwargs):
        kwargs['method'] = 'get'
        super(GetParamsExtractingMixin, self).__init__(*args, **kwargs)


class AjaxActionView(PostParamsExtractingMixin,
                     View):
    """

    """

    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest("Not Ajax request.")

        return self.action(request)
