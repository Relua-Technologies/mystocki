class AsteriskForRequiredFieldsFormMixin:
    add_asterisk = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.add_asterisk:
            self.add_asterisk_to_required_fields()

    def add_asterisk_to_required_fields(self):
        for field_name, field in self.fields.items():
            if field.required:
                if field.label:
                    field.label = f"{field.label}*:"
    
    def add_asterisk_to_field(self, field_name):
        field = self.fields.get(field_name)
        if field.label:
            field.label = f"{field.label}*:"