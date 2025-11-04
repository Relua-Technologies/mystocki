from django.contrib.auth import login
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from apps.authentication.forms import SignInForm
from apps.authentication.apps import APP_NAME


class SingInView(FormView):
    template_name = f'{APP_NAME}/sing_in.html'
    form_class = SignInForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)
