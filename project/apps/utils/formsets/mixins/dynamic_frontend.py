class DynamicFrontendFormsetMixin:
    delete_css_class = 'delete-row'
    add_text = 'Adicionar'
    delete_text = 'Remover'
    add_container_class = None
    delete_container_class = None
    add_css_class = 'add-row'
    delete_css_class = 'delete-row'
    form_css_class = 'dynamic-form'
    extra_classes = []
    keep_field_values = ''
    added = None
    removed = None
    hide_last_add_form = False

    def __init__(self, *args, **kwargs):
        self._set_dynamic_frontend_options(kwargs)
        super().__init__(*args, **kwargs)

    def _set_dynamic_frontend_options(self, kwargs):
        options = [
            'delete_css_class',
            'add_text',
            'delete_text',
            'add_container_class',
            'delete_container_class',
            'add_css_class',
            'delete_css_class',
            'form_css_class',
            'extra_classes',
            'keep_field_values',
            'added',
            'removed',
            'hide_last_add_form',
        ]

        for option in options:
            setattr(self, option, kwargs.pop(option, getattr(self, option)))

    def get_formset_options(self):
        return {
            'prefix': self.get_prefix(),
            'delete-css-class': self.delete_css_class,
            'add-text': self.add_text,
            'delete-text': self.delete_text,
            'add-container-class': self.add_container_class,
            'delete-container-class': self.delete_container_class,
            'add-css-class': self.add_css_class,
            'form-css-class': self.form_css_class,
            'extra-classes': self.extra_classes,
            'keep-field-values': self.keep_field_values,
            'added': self.added,
            'removed': self.removed,
            'hide-last-add-form': str(self.hide_last_add_form).lower(),
        }

    def as_div(self):
        formset_html = super().as_div()
        options = self.get_formset_options()
        data_attrs = ' '.join(f'data-{key}="{value}"' for key, value in options.items())
        return f'<div {data_attrs}>{formset_html}</div>'