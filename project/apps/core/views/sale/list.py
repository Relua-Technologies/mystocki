from apps.core.views.utils.base import BaseListView
from apps.core.views.sale.base import BaseSaleView


class SaleListView(BaseSaleView, BaseListView):
    list_display = [
        'id',
        'date',
        'customer_name',
    ]
    search_fields = list_display