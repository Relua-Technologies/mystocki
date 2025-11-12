from django import forms
from django.forms import inlineformset_factory
from apps.core.models import Sale, SalePayment
from apps.core.forms.utils.base import BaseModelForm
from apps.core.formsets.base import BaseInlineFormSet


class SalePaymentModelForm(BaseModelForm):
    css_classes = 'grid gap-6 mb-6 md:grid-cols-6'

    payment_type = forms.ChoiceField(
        choices=SalePayment.PAYMENT_TYPES,
        label="Forma de Pagamento",
        widget=forms.Select(attrs={"class": "input"})
    )

    target_value = forms.DecimalField(
        label="Valor a Pagar",
        required=True,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            "class": "input text-right",
            "placeholder": "0,00"
        }),
    )

    amount_paid = forms.DecimalField(
        label="Valor Pago",
        required=True,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            "class": "input text-right",
            "placeholder": "0,00"
        }),
    )

    change = forms.DecimalField(
        label="Troco",
        required=False,
        disabled=True,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            "class": "text-gray-700 bg-gray-100 border border-gray-300 rounded-md p-2 text-right",
            "readonly": "readonly",
        }),
    )

    class Meta:
        model = SalePayment
        fields = ["payment_type", "target_value", "amount_paid", "change"]


SalePaymentInlineFormset = inlineformset_factory(
    Sale,
    SalePayment,
    form=SalePaymentModelForm,
    formset=BaseInlineFormSet,
    extra=1,
)

SalePaymentInlineFormset.delete_css_class = "delete-row flex items-end"
SalePaymentInlineFormset.verbose_title = "Pagamentos da Venda"
