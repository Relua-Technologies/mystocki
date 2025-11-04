from django.forms.widgets import TextInput


class CtpsNumberInputWidget(TextInput):
    def __init__(self, attrs={}):
        attrs['class'] = 'ctps-number-input'
        super().__init__(attrs=attrs)
