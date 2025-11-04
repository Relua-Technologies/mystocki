from apps.utils.formsets.base.formset import BaseFormset
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet as DjangoBaseGenericInlineFormSet


class BaseGenericInlineFormSet(BaseFormset, DjangoBaseGenericInlineFormSet):
    pass
