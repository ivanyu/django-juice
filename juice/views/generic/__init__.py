from django import forms
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest

from ..mixins import UrlKwargsMixing


class ConfirmationView(UrlKwargsMixing,
                       FormView):
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
        back = dictionary.get(self.back_url_param_name, None)
        if not back:
            back = self.default_url

        success = dictionary.get(self.success_url_param_name, None)
        if not success:
            success = back
        return (back, success)

    def get_initial(self):
        return {
            'back': self.get_back_url(),
            'success':  self.get_success_url()
        }

    def get_back_url(self):
        return self.back_url

    def get_form_name(self):
        return self.form_name

    def get(self, request, *args, **kwargs):
        self.back_url, self.success_url = self.__extract_urls(request.GET)
        return super(ConfirmationView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super(ConfirmationView, self).get_context_data(**kwargs)
        context_data['form_name'] = self.get_form_name()
        context_data['yes_btn_value'] = 'yes'
        context_data['no_btn_value'] = 'no'
        context_data['back_url'] = self.back_url
        context_data['success_url'] = self.success_url
        return context_data

    def action(self, request):
        pass

    def no(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_back_url())

    def yes(self, request, *args, **kwargs):
        # Skip form validation - not needed.
        self.action(request)
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        self.back_url, self.success_url = self.__extract_urls(request.POST)

        confirm = request.POST.get(self.get_form_name(), None)
        if not confirm or confirm not in ['yes', 'no',]:
            return HttpResponseBadRequest()
        if confirm == 'no':
            return self.no(request)
        return self.yes(request)
