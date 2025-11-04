from django import forms

# Not work with ChoiceField
class RemoveEmptyChoiceLabelFormMixin:
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adjust_empty_labels()

    def adjust_empty_labels(self):
        for field_name, field in self.fields.items():
            if field.required and isinstance(field, (forms.ChoiceField, forms.ModelChoiceField)):
                field.empty_label = None
