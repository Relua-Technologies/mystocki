from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.core.models import SaleItem, StockMovement


@receiver(post_delete, sender=SaleItem)
def delete_stock_movement_from_sale_item(sender, instance: SaleItem, **kwargs):
    content_type = ContentType.objects.get_for_model(SaleItem)
    
    StockMovement.objects.filter(
        related_operation_content_type=content_type,
        related_operation_object_id=instance.id,
        movement_type="OUT",
    ).delete()
