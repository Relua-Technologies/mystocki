from django.db import models
from apps.core.models.utils import BaseModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.utils.get_current_user import get_current_user


class StockMovementManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        user = get_current_user()
        if user and getattr(user, "company_id", None):
            return queryset.filter(item__stock__company_id=user.company_id)
        return queryset.none()


class StockMovement(BaseModel):
    objects = StockMovementManager()

    MOVEMENT_TYPES = (
        ("IN", "Entrada"),
        ("OUT", "Saída"),
    )

    item = models.ForeignKey(
        "Item",
        on_delete=models.CASCADE,
        verbose_name="Item"
    )
    movement_type = models.CharField(
        max_length=3,
        choices=MOVEMENT_TYPES,
        verbose_name="Tipo de Movimento"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Quantidade"
    )
    total_purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço Total da Compra"
    )
    related_operation_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movement_related_operation",
        verbose_name="Tipo da Operação Relacionada"
    )
    related_operation_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID da Operação Relacionada"
    )
    related_operation = GenericForeignKey(
        "related_operation_content_type",
        "related_operation_object_id"
    )

    class Meta:
        db_table = "stock_movement"
        verbose_name = "Movimentação de Estoque"
        verbose_name_plural = "Movimentações de Estoque"

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.item.name}"
