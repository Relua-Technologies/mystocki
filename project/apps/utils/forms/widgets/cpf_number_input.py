from django.forms.widgets import TextInput


class CpfInputNumberWidget(TextInput):
    def __init__(self, attrs={}):
        attrs['class'] = 'cpf-number-input'
        super().__init__(attrs=attrs)
