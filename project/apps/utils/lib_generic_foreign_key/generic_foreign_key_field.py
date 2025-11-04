from django import forms
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
            

class GenericForeignKeyField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.allowed_models = self.get_allowed_models(kwargs)
        self.querysets = self.get_querysets(kwargs)
        self.empty_label = self.get_empty_label(kwargs)
        
        super().__init__(*args, **kwargs)
        self.choices = self.get_choices()

    def get_allowed_models(self, kwargs=None):
        if hasattr(self, 'allowed_models') and self.allowed_models:
            return self.allowed_models

        kwargs = kwargs or {}
        self.allowed_models = kwargs.pop('allowed_models', []) or []
        return self.allowed_models
    
    def get_queryset(self, model):
        return model.objects.all()

    def get_querysets(self, kwargs=None):
        if hasattr(self, 'querysets') and self.querysets:
            return self.querysets

        kwargs = kwargs or {}
        querysets = kwargs.pop('querysets', []) 
        if querysets is None: return []

        self.querysets =  ( 
            [self.get_queryset(model) for model in self.get_allowed_models()]
            if not querysets else 
            querysets
        )
        return self.querysets
    
    def get_empty_label(self, kwargs=None):
        if hasattr(self, 'empty_label') and self.empty_label is not None:
            return self.empty_label

        kwargs = kwargs or {}
        self.empty_label = kwargs.pop('empty_label', '---------')
        return self.empty_label
    
    def get_choices(self):
        choices = []
        
        if self.empty_label is not None:
            choices.append(('', self.empty_label))

        for queryset in self.querysets:
            content_type = ContentType.objects.get_for_model(queryset.model)

            for obj in queryset:
                value = f'{content_type.id}:{obj.pk}'
                label = str(obj)
                choices.append((value, label))

        return choices

    def get_object_from_value(self, value):
        if not value:
            return None
        
        try:
            model_id, object_id = value.split(":")
            
            try:
                content_type = ContentType.objects.get_for_id(model_id)
            except ContentType.DoesNotExist:
                raise ValidationError(f"Content type with ID {model_id} is not allowed or does not exist.")
            
            model_class = content_type.model_class()
            
            if model_class not in self.allowed_models:
                raise ValidationError(f"Content type for model '{content_type.model}' is not allowed.")

            try:
                model_instance = model_class.objects.get(pk=object_id)
            except model_class.DoesNotExist:
                raise ValidationError(f"Object with ID {object_id} not found in the '{model_class._meta.verbose_name}' model.")
            
            return model_instance
        
        except ValueError:
            raise ValidationError('Invalid format for the value. Expected format: model_id:object_id.')
    
    def clean(self, value):
        return self.get_object_from_value(value)

    def to_python(self, value):
        return self.get_object_from_value(value)