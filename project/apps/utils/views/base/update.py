from django.views.generic import UpdateView
from .base import BaseModelView


class BaseUpdateView(BaseModelView, UpdateView):
    operation_mode = 'Atualização'
    template_name = '_update.html'
