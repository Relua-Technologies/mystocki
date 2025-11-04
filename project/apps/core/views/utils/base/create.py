from django.views.generic import CreateView
from .base import BaseModelView


class BaseCreateView(BaseModelView, CreateView):
    operation_mode = 'Criação'
    template_name = '_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs