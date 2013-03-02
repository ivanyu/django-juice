# -*- coding: utf-8 -*-
"""
Generic views for different purposes.

`ConfirmationView` - a generic view which helps solve a problem of showing
confirmation forms for different actions.
"""

from .confirmation import ConfirmationView
from .ajax_action import (AjaxActionView, ParamExtractionError)

__all__ = ['ConfirmationView',
           'AjaxActionView', 'ParamExtractionError']
