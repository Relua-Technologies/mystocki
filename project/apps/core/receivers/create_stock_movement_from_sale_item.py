from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.core.models import SaleItem, StockMovement


@receiver(post_save, sender=SaleItem)
def create_stock_movement_from_sale_item(sender, instance, created, **kwargs):
    content_type = ContentType.objects.get_for_model(instance)

    exists = StockMovement.objects.filter(
        related_operation_content_type=content_type,
        related_operation_object_id=instance.id
    ).exists()

    if not exists:
        StockMovement.objects.create(
            item=instance.item,
            movement_type="OUT",
            quantity=instance.quantity,
            related_operation_content_type=content_type,
            related_operation_object_id=instance.id,
        )
