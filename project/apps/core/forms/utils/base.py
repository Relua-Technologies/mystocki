from django import forms
from apps.core.forms.utils.mixins import AsteriskForRequiredFieldsFormMixin
from django_remote_form_helpers.forms.mixins import APIFieldsHandlerFormMixin


class BaseModelForm(APIFieldsHandlerFormMixin, AsteriskForRequiredFieldsFormMixin, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.reload_dynamic_querysets()

    def reload_dynamic_querysets(self):
        for name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                model_class = field.queryset.model
                if hasattr(model_class.objects, "for_company"):
                    company_id = getattr(self.user, "company_id", None)
                    if company_id:
                        field.queryset = model_class.objects.for_company(company_id)
                        continue
                if hasattr(model_class.objects, "get_queryset"):
                    try:
                        field.queryset = model_class.objects.all()
                    except Exception:
                        pass
                field.queryset = field.queryset.all()

    # Temporary fix for the Django django-remote-form-helpers library
    def initialize_api_fields(self):
        if not self.is_bound:
            instance_pk = getattr(self.instance, 'pk', None)

            for field_name in self.API_FIELDS:
                form_field = self.fields.get(field_name)
                initial_value = self.initial.get(field_name, None)
                
                if isinstance(form_field, forms.ModelChoiceField):                
                    if initial_value is None and instance_pk:
                        initial_value = getattr(self.instance, field_name, None)
                    
                    if initial_value is not None:
                        model_class = form_field.queryset.model
                        queryset = ( 
                            model_class.objects.filter(pk=initial_value.pk)
                            if  isinstance(initial_value, model_class) else
                            model_class.objects.filter(pk=initial_value)
                        )
                        form_field.queryset = queryset

    def set_generic_choices(self, field_name, name_field):
        field = self.fields.get(field_name)
        if not field:
            return

        instance = getattr(self.instance, field_name, None)
        initial_value = self.initial.get(field_name)

        if not initial_value or not self.instance.pk:
            return

        field.choices = [(initial_value, getattr(instance, name_field))]