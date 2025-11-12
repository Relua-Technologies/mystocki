from django.forms import BaseInlineFormSet as DjangoBaseInlineFormSet
from apps.utils.formsets.base.formset import BaseFormset
from apps.utils.formsets.mixins import AutoExtraFormSetMixin


class BaseInlineFormSet(BaseFormset, DjangoBaseInlineFormSet, AutoExtraFormSetMixin):
    pass