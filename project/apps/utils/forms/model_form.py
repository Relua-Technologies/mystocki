from django import forms
from apps.utils.forms.mixins import AsteriskForRequiredFieldsFormMixin
from django_remote_form_helpers.forms.mixins import APIFieldsHandlerFormMixin
from apps.utils.lib_generic_foreign_key import GenericForeignKeyHandlerModelFormMixin


class BaseModelForm(GenericForeignKeyHandlerModelFormMixin, APIFieldsHandlerFormMixin, AsteriskForRequiredFieldsFormMixin, forms.ModelForm):

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

    def get_field_text(self, text_path, related_instance):
        if text_path.lower() not in ['__str__']:
            field_parts = text_path.split('__') 

            for part in field_parts:
                related_instance = getattr(related_instance, part)
                if related_instance is None:
                    raise AttributeError(f"'{type(related_instance).__name__}' object has no attribute '{part}'")
        return related_instance
        
    def set_generic_choices(self, field_name, text_path):
        instance = self.instance
        if not instance.pk:
            return
        
        field = self.fields.get(field_name)
        if not field:
            return

        initial_value = self.initial.get(field_name)

        if not initial_value:
            return
        
        related_instance = getattr(instance, field_name)
        field_text = self.get_field_text(text_path, related_instance)
        field.choices = [(initial_value, field_text)]
