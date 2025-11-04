from apps.core.apps import APP_NAME
from django.urls import reverse_lazy
from apps.core.models import StockMovement
from apps.core.forms import StockMovementForm


class BaseStockMovementView:
    model = StockMovement
    form_class = StockMovementForm
    url_name = f'{APP_NAME}:stock_movement'

    def get_success_url(self) -> str:
        return reverse_lazy(f'{self.url_name}_list')    