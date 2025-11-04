from django.forms.widgets import TextInput


class TelephoneInputWidget(TextInput):
    def __init__(self, attrs={}):
        attrs['class'] = 'telephone-input'
        super().__init__(attrs=attrs)
