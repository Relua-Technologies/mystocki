from apps.core.forms.utils.base import BaseModelForm
from apps.core.models import StockMovement


class StockMovementForm(BaseModelForm):
    class Meta:
        model = StockMovement
        fields = [
            "item",
            "movement_type",
            "quantity",
            "total_purchase_price",
        ]