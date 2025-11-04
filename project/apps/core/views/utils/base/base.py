from apps.core.views.utils.mixins.extends_template_name import ExtendsTemplateViewMixin
from django.views.generic import TemplateView, View
from apps.core.apps import APP_NAME
from django.shortcuts import render


class BaseView(View):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_sidebar'] = True
        return context
    

class BaseModelView(BaseView):
    model = None
    operation_mode = None
    verbose_name = None
    verbose_name_plural = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['operation_mode'] = self.get_operational_mode()
        context['verbose_name'] = self.get_verbose_name()
        context['verbose_name_plural'] = self.get_verbose_name_plural()
        context['model'] = self.get_model()
        return context
    
    def get_model(self):
        model = getattr(self, 'model', None)
        if model is None:
            form_class = getattr(self, 'form_class', None)
            model = form_class._meta.model
        return model

    def get_operational_mode(self):
        return self.operation_mode

    def get_verbose_name(self):
        return self.verbose_name
    
    def get_verbose_name_plural(self):
        return self.verbose_name_plural