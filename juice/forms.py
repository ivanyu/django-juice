# -*- coding: utf-8 -*-
"""
A collection of form utils.

`TrimCharField` - a char field which truncates it's value to max_length before
validation.
"""
from __future__ import unicode_literals
from django.forms import CharField


class TrimCharField(CharField):
    """
    A char field which truncates it's value to max_length before validation.
    """

    def to_python(self, value):
        py_value = super(TrimCharField, self).to_python(value)
        # Max_length can be 0.
        if self.max_length is not None:
            py_value = py_value[:self.max_length]
        return py_value
