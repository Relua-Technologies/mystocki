from django.views.generic import UpdateView
from .base import BaseModelView


class BaseUpdateView(BaseModelView, UpdateView):
    operation_mode = 'Atualização'
    template_name = '_update.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs