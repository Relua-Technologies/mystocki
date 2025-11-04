from django import forms
from apps.core.models import Item, Sale, SaleItem
from django.forms import inlineformset_factory, BaseInlineFormSet
from apps.core.forms.utils.base import BaseModelForm


class ItemSelectWithPrice(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if value:  
            option["attrs"]["data-price"] = float(value.instance.sale_price)
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
        queryset=Item.objects.all(),
        widget=ItemSelectWithPrice(
            attrs={
                "class": "input",
            }
        ),
        label="Item",
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["item"].queryset = Item.objects.in_stock()

    class Meta:
        model = SaleItem
        fields = ["item", "quantity", "discount", "price", "total"]



SaleItemInlineFormset = inlineformset_factory(
    Sale,
    SaleItem,
    form=SaleItemModelForm,
    extra=1,
)

SaleItemInlineFormset.delete_css_class = "delete-row flex items-end"
SaleItemInlineFormset.verbose_title = "Itens da Venda"