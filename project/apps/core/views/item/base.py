from apps.core.apps import APP_NAME
from django.urls import reverse_lazy
from apps.core.models import Item
from apps.core.forms import ItemForm


class BaseItemView:
    model = Item
    form_class = ItemForm
    url_name = f'{APP_NAME}:item'

    def get_success_url(self) -> str:
        return reverse_lazy(f'{self.url_name}_list')    