from apps.core.views.stock_movement.base import BaseStockMovementView
from apps.core.views.utils.base import BaseListView


class StockMovementListView(BaseStockMovementView, BaseListView):
    list_display = [
        "item__name",
        "movement_type",
        "quantity",
        "total_purchase_price",
    ]
    search_fields = list_display