# -*- coding: utf-8 -*-
"""
Form utilities.

`TrimCharField` - a char field which truncates it's value to max_length before
validation.
"""
from __future__ import unicode_literals

from django.forms import CharField
from django.forms import ModelForm
from django.forms.models import ModelFormMetaclass
from django.core.exceptions import ImproperlyConfigured


class TrimCharField(CharField):
    """
    A char field which truncates it's value to `max_length` before validation.
    """

    def to_python(self, value):
        py_value = super(TrimCharField, self).to_python(value)
        # Max_length can be 0.
        if self.max_length is not None:
            py_value = py_value[:self.max_length]
        return py_value


class TrimCharFieldsModelFormMetaclass(ModelFormMetaclass):
    """
    A metaclass for ModelForm which replaces `CharField` with `TrimCharField`
    for fields listed in `Meta.trim_fields`.

    Example:

        class UserProfileForm(six.with_metaclass(
            TrimCharFieldsModelFormMetaclass, forms.ModelForm)):
            class Meta:
                model = UserProfile
                fields = ('real_name', 'about', )
                trim_fields = ('about', )

            # the rest of Meta and UserProfileForm

    In this Example two fields (`real_name` and `about`) will be taken from
    UserProfile. But we want to make `about` field able to trim posted value
    to `max_length` instead of raiseing exception. So we add it to `trim_fields`
    and the metaclass will replace its `CharField` with `TrimCharField` using
    all `CharField`'s parameters (`label`, `required`, `widget` etc.)
    """

    def __new__(cls, name, bases, attrs):
        new_class = super(TrimCharFieldsModelFormMetaclass, cls).__new__(
            cls, name, bases, attrs)

        # Raise an exception in case the metaclass used with not
        if not issubclass(new_class, ModelForm):
            raise TypeError("Class '{}' must be derived from ModelForm".
                format(name))

        # Ignore NewBase class inserted by six. Also we're not interested in
        # classes without Meta.
        if name == 'NewBase' or 'Meta' not in attrs:
            return new_class

        trim_fields = attrs['Meta'].__dict__.get('trim_fields', [])

        for f in trim_fields:
            if f not in new_class.base_fields:
                raise ImproperlyConfigured(
                    "Trim field '{}' doesn't exist in base_fields.".format(f))

            field = new_class.base_fields[f]
            if not isinstance(field, CharField):
                raise TypeError(
                    "Trim field '{}' must be CharField, {} given.".format(
                        f, field.__class__.__name__))

            trimField = TrimCharField(
                required=field.required,
                label=field.label,
                initial=field.initial,
                widget=field.widget,
                error_messages=field.error_messages,
                validators=field.validators,
                localize=field.localize,
                max_length=field.max_length,
                min_length=field.min_length
                )
            new_class.base_fields[f] = trimField

        return new_class
