from django import forms


class NumericTextInputWidget(forms.TextInput):
    def __init__(self, attrs=None):
        default_attrs = {'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
