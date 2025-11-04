from django.views.generic import DetailView
from .base import BaseModelView


class BaseDetailView(BaseModelView, DetailView):
    operation_mode = 'Detalhe'
    template_name = '_detail.html'
