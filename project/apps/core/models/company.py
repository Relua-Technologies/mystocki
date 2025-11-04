from django.db import models
from apps.core.models.utils import BaseModel


class Company(BaseModel):
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, blank=True, null=True)

    class Meta:
        db_table = "company"

    def __str__(self):
        return self.name
