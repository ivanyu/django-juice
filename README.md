django-juice
============

A collection of small reusable Django utilities in form of Django app.

Mixins:
* `LoginRequiredMixin` - a mixin which makes class-based view available only for authenticated users.
* `StoreArgsBeforeDispatchMixin` - a mixin which stores `args` and `kwargs` in `self` before dispatching. Useful in Django <=1.4.
* `GetObjectOnceMixin`- a mixin which prevents `get_object` from make more than one call to databese even in case of many calls.
* `UrlKwargsMixing` - a mixin which extracts required kwargs from the url and makes them available inside a view as attributes.

Form utils:
* `TrimCharField` - a char field which truncates it's value to `max_length` before validation.
* `TrimCharFieldsModelFormMetaclass` - a metaclass for ModelForm which replaces `CharField` with `TrimCharField` for fields listed in `Meta.trim_fields`.

License
=======
The application is distributed under MIT license (see LICENSE.txt).

Contributing
============

Feel free to fork the repository, make changes and pull requests and propose new features.

The project initially started by Ivan Yurchenko.
