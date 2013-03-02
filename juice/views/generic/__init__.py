# -*- coding: utf-8 -*-
"""
Generic views for different purposes.
"""

from django import forms
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest

from ..mixins import UrlKwargsMixing


class ConfirmationView(UrlKwargsMixing,
                       FormView):
    """
    A generic view which helps solve a problem of showing confirmation form
    for different actions.

    It's supposed you want to show a form with two buttons "Yes" and "No" and
    possibly some other content. Also it's supposed that after confirmation or
    rejection user must be redirected somewhere.

    The view workflow is the following.

    1. User goes to view's URL by GET method. It's possible to pass back and
    success URLs (which will be used for redirect later) as GET parameters.
    Default names of these parameters are *back* and *success*. These names can
    be overriden by *back_url_param_name* and *success_url_param_name*
    attributes.
    If back URL isn't passed it's set to default URL (defined by *default_url*
    attribute). If success URL isn't passed it's set to the same value as back
    URL.

    2. A dummy form is displayed to the user. The purpose of the form is to
    store CSRF token and back and success URLs.
    The template is determined by *template_name* attribute and
    *get_template_names* method.
    The context of template rendering consists of:
        * *form* - a form with hidden inputs contains back and success URLs.
        * *form_name* determined by *form_name* attribute and *get_form_name*
        method (default is "_confirm");
        * *yes_btn_value* - the value indicates pressing "Yes" button (default
        is "yes");
        * *no_btn_value* - the value indicates pressing "No" button (default
        is "no");
        * *back_url* and *success_url* - values of back and success URLs
        respectively.

    Template instructions for typical use.
    You should output a `<form>` tag with `method="post"` and `action=""`.
    Inside it you should render *csrf_token*, *form* and buttons. The buttons
    should be output as `<button>` tag with `type="submit"`,
    `name={{ form_name }}` and `value={{ yes_btn_value }}` or
    `value={{ no_btn_value }}` respectively to the button type.
    Example:
        <form method="post" action="">
            {% csrf_token %}
            {{ form }}
            <button type="submit" name="{{ form_name }}"
                    value="{{ no_btn_value }}">No</button>
            <button type="submit" name="{{ form_name }}"
                    value="{{ yes_btn_value }}">Yes</button>
        </form>

    In fact, the "No" button can be rendered as a link to *back_url*. In this
    case won't cause sending of POST request.

    3. User clicks on "Yes" or "No" button. The POST request is sent back to
    the view.
    If user clicked "No" the rediret response to back URL is returned to his
    browser. In case he clicked "Yes" the action determined by *action* method
    is performed and rediret response to success URL is returned to the
    browser.

    To sum up, in the most typical use case you should define in descendant
    view:
    * *template_name* attribute and/or *get_template_names* method;
    * *action* method of the action which performing you want to be confirmed.
    """

    class __Form(forms.Form):
        back = forms.CharField(max_length=100,
                               widget=forms.HiddenInput(),
                               required=False)
        success = forms.CharField(max_length=100,
                                  widget=forms.HiddenInput(),
                                  required=False)

    back_url_param_name = 'back'
    success_url_param_name = 'success'

    default_url = '/'

    form_class = __Form
    form_name = '_confirm'

    def __extract_urls(self, dictionary):
        """
        Extract back and success URLs from `dictionary` (most likely `POST`
        dictionary).

        If back URL is not found it's set to `default_url`.
        If success URL is not found it's set to back URL.
        """
        back = dictionary.get(self.back_url_param_name, None)
        if not back:
            back = self.default_url

        success = dictionary.get(self.success_url_param_name, None)
        if not success:
            success = back
        return (back, success)

    def get_initial(self):
        """
        Get initial values for the form.
        """
        return {
            'back': self.get_back_url(),
            'success':  self.get_success_url()
        }

    def get_back_url(self):
        return self.back_url

    def get_form_name(self):
        return self.form_name

    def get_context_data(self, **kwargs):
        context_data = super(ConfirmationView, self).get_context_data(**kwargs)
        context_data['form_name'] = self.get_form_name()
        context_data['yes_btn_value'] = 'yes'
        context_data['no_btn_value'] = 'no'
        context_data['back_url'] = self.back_url
        context_data['success_url'] = self.success_url
        return context_data

    def action(self, request):
        """
        Action to do in case of confirmation.
        """
        pass

    def no(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_back_url())

    def yes(self, request, *args, **kwargs):
        # Skip form validation - not needed.
        self.action(request)
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.back_url, self.success_url = self.__extract_urls(request.GET)
        return super(ConfirmationView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.back_url, self.success_url = self.__extract_urls(request.POST)

        confirm = request.POST.get(self.get_form_name(), None)
        if not confirm or confirm not in ['yes', 'no']:
            return HttpResponseBadRequest()
        if confirm == 'no':
            return self.no(request)
        return self.yes(request)
