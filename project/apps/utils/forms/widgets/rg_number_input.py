from django.forms.widgets import TextInput


class RgInputNumberWidget(TextInput):
    def __init__(self, attrs={}):
        attrs['class'] = 'rg-number-input'
        super().__init__(attrs=attrs)
