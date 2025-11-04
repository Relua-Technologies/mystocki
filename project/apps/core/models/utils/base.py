from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def isFieldByName(cls, field_name):
        for field in cls._meta.fields:
            if field.name == field_name:
                return True
        return False

    @property
    def model_name(self):
        return self._meta.model_name
        
    @property
    def verbose_name(self):
        return self._meta.verbose_name

    @property
    def verbose_name_plural(self):
        return self._meta.verbose_name_plural

    @classmethod
    def get_field_name_verbose(cls, field_name):
        field = cls._meta.get_field(field_name)
        return field.verbose_name if field else field_name

    class Meta:
        abstract = True