from django.forms.widgets import TextInput


class CnpjNumberInputWidget(TextInput):
    def __init__(self, attrs={}):
        attrs['class'] = 'cnpj-number-input'
        super().__init__(attrs=attrs)
