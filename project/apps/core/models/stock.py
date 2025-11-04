from django.db import models
from apps.core.models.utils import BaseModel


class Stock(BaseModel):
    company = models.ForeignKey("Company", on_delete=models.CASCADE)

    class Meta:
        db_table = "stock"

    def __str__(self):
        return f"Stock #{self.id} - {self.company.name}"
