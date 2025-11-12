from django import forms
from apps.core.models import Item, Sale, SaleItem
from django.forms import inlineformset_factory, BaseInlineFormSet
from apps.core.forms.utils.base import BaseModelForm
from apps.core.formsets.base import BaseInlineFormSet
from apps.core.services import StockService


class ItemSelectWithPrice(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:  
            instance = value.instance
            option["attrs"]["data-price"] = float(instance.sale_price)
            option["attrs"]["data-quantity"] = StockService.get_item_quantity(instance)
            option["attrs"]["data-unit"] = instance.unit_of_measure
        return option


class SaleItemModelForm(BaseModelForm):
    css_classes = 'grid gap-6 mb-6 md:grid-cols-6'

    price = forms.DecimalField(
        label="Preço",
        required=False,
        disabled=True,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(
            attrs={
                "class": "text-gray-700 bg-gray-100 border border-gray-300 rounded-md p-2",
                "readonly": "readonly",
            }
        ),
    )
    total = forms.DecimalField(
        label="Total",
        required=False,
        disabled=True,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(
            attrs={
                "class": "text-gray-700 bg-gray-100 border border-gray-300 rounded-md p-2",
                "readonly": "readonly",
            }
        ),
    )

    item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
        widget=ItemSelectWithPrice(
            attrs={
                "class": "input",
            }
        ),
        label="Item",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["item"].queryset = Item.objects.with_sale_price()

    class Meta:
        model = SaleItem
        fields = ["item", "quantity", "discount", "price", "total"]



SaleItemInlineFormset = inlineformset_factory(
    Sale,
    SaleItem,
    form=SaleItemModelForm,
    formset=BaseInlineFormSet,
    extra=1,
)

SaleItemInlineFormset.delete_css_class = "delete-row flex items-end"
SaleItemInlineFormset.verbose_title = "Itens da Venda"