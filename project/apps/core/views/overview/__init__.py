from django.views.generic import TemplateView
from apps.core.views.utils.base import BaseView


class OverviewView(BaseView, TemplateView):
    template_name = 'app/overview/main.html'