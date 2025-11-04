from django.forms.widgets import TextInput


class BrazilianCellPhoneNumberInputWidget(TextInput):
    template_name = 'utils/forms/widgets/phone_number.html'

    def __init__(self, attrs={}):
        attrs['class'] = 'brazilian-cell-phone-number-input'
        super().__init__(attrs=attrs)
