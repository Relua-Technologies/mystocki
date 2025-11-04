from django.forms.widgets import TextInput


class TeRegistrationNumberInputWidget(TextInput):
    def __init__(self, attrs={}):
        attrs['class'] = 'te-registration-number-input'
        super().__init__(attrs=attrs)
