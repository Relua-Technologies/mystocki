from django.contrib.contenttypes.models import ContentType
from apps.utils.lib_generic_foreign_key.generic_foreign_key_field import GenericForeignKeyField


class GenericForeignKeyHandlerModelFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            for field_name, field in self.fields.items():
                if isinstance(field, GenericForeignKeyField):
                    related_instance = getattr(self.instance, field_name, None)
                    if related_instance:
                        content_type = ContentType.objects.get_for_model(related_instance.__class__)
                        self.initial[field_name] = f'{content_type.id}:{related_instance.pk}'

    def _post_clean(self):
        super()._post_clean()  

        for field_name, field in self.fields.items():
            if isinstance(field, GenericForeignKeyField):
                value = self.cleaned_data.get(field_name)
                setattr(self.instance, field_name, value) 
