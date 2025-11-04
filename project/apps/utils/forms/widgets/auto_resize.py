
from django import forms


class AutoResizeInput(forms.Widget):
    width_unit = None

    def get_width_unit(self, *args, **kwargs):
        if self.width_unit is None:
            raise NotImplementedError("The width unit needs to be defined.")
        return self.width_unit

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        width_unit = self.get_width_unit() 

        initial_length = len(str(value)) if value else len(self.attrs.get('placeholder', '1'))
        context['widget']['attrs'].update({
            'style': f'width: {max(initial_length, 1)}{width_unit};',
            'oninput': (
                'this.style.width = Math.max('
                f'(this.value.length || this.placeholder.length), 1) + "{width_unit}";'
            ),
        })
        return context


class AutoResizeTextInput(AutoResizeInput, forms.TextInput):
    width_unit = 'em'


class AutoResizeNumberInput(AutoResizeInput, forms.NumberInput):
    width_unit = 'ch'
