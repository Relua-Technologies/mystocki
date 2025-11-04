from django.db import models
from apps.core.models.utils import BaseModel
from django.conf import settings
from django.utils import timezone
from apps.utils.get_current_user import get_current_user


class SaleManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        user = get_current_user()
        if user and getattr(user, "company_id", None):
            return queryset.filter(company_id=user.company_id)
        return queryset.none()
    

class Sale(BaseModel):
    objects = SaleManager()

    company = models.ForeignKey("Company", on_delete=models.CASCADE, verbose_name="Empresa")
    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Vendido por"
    )
    items = models.ManyToManyField("Item", through="SaleItem", verbose_name="Itens")
    date = models.DateField(default=timezone.now, verbose_name="Data da Venda")
    customer_name = models.CharField(
        max_length=255,
        verbose_name="Nome do Cliente",
        blank=True,
        null=True
    )
    note = models.TextField(blank=True, null=True, verbose_name="Observações")

    class Meta:
        db_table = "sale"
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

    def __str__(self):
        return f"Sale #{self.id} - {self.company.name}"
