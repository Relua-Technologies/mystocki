from django.views.generic import CreateView
from .base import BaseModelView


class BaseCreateView(BaseModelView, CreateView):
    operation_mode = 'Criação'
    template_name = '_create.html'
