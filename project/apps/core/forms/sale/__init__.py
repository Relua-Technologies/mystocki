from django import forms
from django_formsets_inside_form import FormsetsInsideFormMixin
from apps.core.forms.utils.base import BaseModelForm
from apps.core.models import Sale
from apps.core.forms.sale.formsets.sale_item import SaleItemInlineFormset
from apps.core.apps import APP_NAME


class SaleForm(FormsetsInsideFormMixin, BaseModelForm):
    # template_name = f"{APP_NAME}/sale/form_div.html"

    class Meta:
        model = Sale
        fields = [
            "customer_name",
            "date",
            "note",
        ]
        widgets = {
            "note": forms.Textarea(attrs={"rows": 1}),
        }

    def save_instance(self, commit=True, *args, **kwargs):
        instance = super().save_instance(commit=False, *args, **kwargs)
        if hasattr(self, "user") and self.user:
            instance.sold_by = self.user
            instance.company_id = getattr(self.user, "company_id", None)

        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def save_formsets(self, instance, *args, **kwargs):
        for formset in self.formsets.values():
            formset.is_valid()
            formset.instance = instance
            formset.save()
            
    def get_formsets(self, formsets={}, instance=None, *args, **kwargs):
        formsets = {
            "sale_items": SaleItemInlineFormset(
                data=self.data if self.is_bound else None,
                files=self.files if self.is_bound else None,
                instance=instance,
                prefix="sale_items",
            ),
        }
        return formsets
