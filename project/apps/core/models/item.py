from django.db import models
from apps.core.models.utils import BaseModel
from apps.utils.get_current_user import get_current_user


class ItemManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        user = get_current_user()

        if user and getattr(user, "company_id", None):
            return queryset.filter(stock__company_id=user.company_id)

        return queryset.none()

    def in_stock(self):
        from apps.core.services import StockService

        base_queryset = self.get_queryset()
        items = list(base_queryset)
        quantities = StockService.get_items_quantities(items)

        item_ids_in_stock = [
            item.id for item in items if quantities.get(item.id, 0) > 0
        ]

        return base_queryset.filter(id__in=item_ids_in_stock)
    

class Item(BaseModel):
    objects = ItemManager()

    UNIT_CHOICES = [
        ("un", "Un"),
        ("kg", "Kg"),
        ("g", "G"),
        ("l", "L"),
        ("ml", "Ml"),
        ("cx", "Cx"),
        ("pc", "Pc"),
    ]

    stock = models.ForeignKey(
        "Stock",
        on_delete=models.CASCADE,
        verbose_name="Estoque"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Nome"
    )
    unit_of_measure = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        default="un",
        verbose_name="Unidade de Medida"
    )
    sale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço de Venda",
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "item"
        verbose_name = "Item"
        verbose_name_plural = "Itens"

    def __str__(self):
        return f"{self.name} ({self.get_unit_of_measure_display()})"
