from django.core.exceptions import ValidationError
from apps.core.forms.utils.base import BaseModelForm
from apps.core.models import Item, Stock


class ItemForm(BaseModelForm):
    class Meta:
        model = Item
        fields = [
            "code",
            "name",
            "unit_of_measure",
            "sale_price",
            "stock",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_stock_queryset_and_initial()

    def _set_stock_queryset_and_initial(self):
        if not self.user or not getattr(self.user, "company", None):
            raise ValidationError("User must be associated with a company.")

        queryset = Stock.objects.filter(company=self.user.company)
        if not queryset.exists():
            raise ValidationError("No stock found for the user's company.")

        self.fields["stock"].queryset = queryset

        if queryset.count() == 1:
            self.fields["stock"].initial = queryset.first()
