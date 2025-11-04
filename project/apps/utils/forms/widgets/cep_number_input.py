from django.forms.widgets import TextInput


class CepNumberInputWidget(TextInput):
    def __init__(self, attrs={}):
        attrs['class'] = 'cep-number-input'
        super().__init__(attrs=attrs)
