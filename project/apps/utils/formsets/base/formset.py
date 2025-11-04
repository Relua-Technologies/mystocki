from django.forms import BaseFormSet as DjangoBaseFormset
from apps.utils.formsets.mixins import DynamicFrontendFormsetMixin, AutoExtraFormSetMixin


class BaseFormset(DynamicFrontendFormsetMixin, AutoExtraFormSetMixin, DjangoBaseFormset):
    pass