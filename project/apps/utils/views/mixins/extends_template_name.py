class ExtendsTemplateViewMixin:
    extends_template_name = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['extends_template_name'] = self.get_extends_template_name()
        return context
    
    def get_extends_template_name(self):
        return self.extends_template_name
