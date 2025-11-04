from apps.utils.formsets.base.formset import BaseFormset
from django.forms import BaseInlineFormSet as DjangoBaseInlineFormSet


class BaseInlineFormSet(BaseFormset, DjangoBaseInlineFormSet):
    pass