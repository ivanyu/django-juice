# -*- coding: utf-8 -*-
"""
A colliction of view mixins.

`LoginRequiredMixin` - a mixin which makes class-based view available only for
authenticated users.

`StoreArgsBeforeDispatchMixin` - a mixin which stores `args` and `kwargs` in
`self` before dispatching. Useful in Django <=1.4.

`GetObjectOnceMixin` - a mixin which prevents `get_object` from make more than
one call to databese even in case of many calls.

`UrlKwargsMixing` - a mixin which extracts required kwargs from the url and
makes them available inside a view as attributes.
"""
from __future__ import unicode_literals
from types import MethodType

from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import six


class LoginRequiredMixin(object):
    """
    A view mixin which makes class-based view available only for authenticated
    users by applying Django's login_required decorator.
    The mixin must be the first (the left-most) in view's superclass list.

    Example:

        class MyView(LoginRequiredMixin, <other mixins>, DetailView):
            # ... class content ...
    """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class StoreArgsBeforeDispatchMixin(object):
    """
    A mixin which stores `args` and `kwargs` in `self` before dispatching.

    The mixin must stay in bases list before any mixin or base class which
    needs accessing to `self.args` or `self.kwargs` before call of
    `View`'s `dispatch`.

    It's useful for Django <=1.4 because in it `args` and `kwargs` are assigned
    to self only in `View`'s `dispatch` method which make them inaccessible
    before this call.

    Django >=1.5 assigns arguments to self in the wrapper returned by `as_view`
    so this mixin is useless.
    """

    def dispatch(self, request, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        return super(StoreArgsBeforeDispatchMixin, self).dispatch(
            request, *args, **kwargs)


class GetObjectOnceMixin(object):
    """
    A mixin which prevents `get_object` from make more than one call to
    databese even in case of many calls.
    """
    
    def get_object(self, queryset=None):
        if hasattr(self, 'object'):
            return self.object

        return super(GetObjectOnceMixin, self).get_object(queryset)


class UrlKwargsMixing(object):
    """
    A view mixin which extracts required kwargs from the url and makes them
    available inside a view as attributes.

    The mixin's behaviour is determined by the following attributes.

    `url_kwargs` - the list of required kwargs. An elements of the list can be:
        * a tuple in (kwarg, attr_name) format;
        * a string with kwarg name. In this case attr_name will be kwarg name
          with '_' prefix.

    `url_kwargs_mandatory` - the flag of the kwargs mandatoriness. If it's set
    to `True` (default) the `TypeError` exception will be raised in case one of
    the kwargs is absent. In case it's `False` the missing kwarg will be
    silently ignored.

    `url_kwargs_on_attr_collision` - the strategy in case of possible
    attributes collisions (when an attribute with name `attr_name` already
    exists). If it's set to `raise` (default) the `ImproperlyConfigured`
    exception will be raised in case of collision. If the value is `overwrite`
    the existing attribute will be overwritten (not recommended).

    Example:

        # in urls.py
        # ...
        url(r'^(?P<username>\w+)/feed/(?P<feed_number>)/$',
            views.UserFeedView.as_view())
        # ...

        class UserFeedView(UrlKwargsMixing, <other mixins>, DetailView):
            url_kwargs = [ 'username', ('feed_number', '_feed_n')]

            # ...

            def get_queryset(self):
                # Here self._username and self._feed_n is accessible and have
                # values extracted from the url regexp.
    """

    url_kwargs = []
    url_kwargs_mandatory = True
    url_kwargs_on_attr_collision = 'raise'


    def __init__(self, *args, **kwargs):
        # Check configuration.
        if self.url_kwargs_on_attr_collision not in ['raise', 'overwrite']:
            msg = ("Unknown attribute collision behaviour '{}'. "
                   "Use 'raise' or 'overwrite'."
                   .format(self.url_kwargs_on_attr_collision))
            raise ImproperlyConfigured(msg)            

        # Define two processing strategies - for 'raise' and for 'overwrite'.
        req_msg_tpl = "Keyword argument '{}' is required but not provided."

        def raise_strategy(self, kwarg, kwargs, attr_name):
            if kwarg not in kwargs:
                if self.url_kwargs_required:
                    raise TypeError(req_msg_tpl.format(kwarg))
                return
            if hasattr(self, attr_name):
                raise ImproperlyConfigured(
                    "Attribute '{}' is alreay exists.".format(attr_name))
            setattr(self, attr_name, kwargs[kwarg])

        def overwrite_strategy(self, kwarg, kwargs, attr_name):
            if kwarg not in kwargs:
                if self.url_kwargs_required:
                    raise TypeError(req_msg_tpl.format(kwarg))
                return
            setattr(self, attr_name, kwargs[kwarg])

        # Choose processing strategy.
        fname = self.url_kwargs_on_attr_collision + '_strategy'
        self.__process = MethodType(locals()[fname], self)

        # Normalize kwargs - convert strings into tuples.
        normalized_kwargs = []
        for el in self.url_kwargs:
            if isinstance(el, six.string_types):
                normalized_kwargs.append((el, '_'+el, ))
            else:
                normalized_kwargs.append(el)
        self.url_kwargs = normalized_kwargs

        super(UrlKwargsMixing, self).__init__(*args, **kwargs)


    def dispatch(self, request, *args, **kwargs):
        for kwarg, attr_name in self.url_kwargs:
            self.__process(kwarg, kwargs, attr_name)

        return super(UrlKwargsMixing, self).dispatch(request, *args, **kwargs)
