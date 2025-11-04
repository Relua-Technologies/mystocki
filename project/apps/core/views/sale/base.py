from apps.core.apps import APP_NAME
from django.urls import reverse_lazy
from apps.core.models import Sale
from apps.core.forms.sale import SaleForm


class BaseSaleView:
    model = Sale
    form_class = SaleForm
    url_name = f'{APP_NAME}:sale'

    def get_success_url(self) -> str:
        return reverse_lazy(f'{self.url_name}_list')    