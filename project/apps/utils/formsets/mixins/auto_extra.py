class AutoExtraFormSetMixin:
    ignore_extra_setting = True

    def total_form_count(self):
        if self.ignore_extra_setting:
            initial_forms = self.initial_form_count()
            self.extra = 0 if initial_forms else 1

        return super().total_form_count()