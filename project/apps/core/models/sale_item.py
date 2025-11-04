from django.db import models
from apps.core.models.utils import BaseModel


class SaleItem(BaseModel):
    sale = models.ForeignKey("Sale", on_delete=models.CASCADE, verbose_name="Venda")
    item = models.ForeignKey("Item", on_delete=models.CASCADE, verbose_name="Item")
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade"
    )
    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Desconto"
    )

    class Meta:
        db_table = "sale_item"
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"

    @property
    def total(self):
        return (self.item.sale_price - self.discount) * self.quantity

    def __str__(self):
        return f"{self.item.name} ({self.quantity} {self.item.unit_of_measure})"
