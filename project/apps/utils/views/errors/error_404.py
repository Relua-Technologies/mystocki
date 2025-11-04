from django.views.generic.base import TemplateView


class Error404View(TemplateView):
    template_name = 'utils/errors/404.html'
    