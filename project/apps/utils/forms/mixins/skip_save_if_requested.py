class SkipSaveIfRequestedFormMixin:
    def __init__(self, *args, **kwargs):
        self.skip_save = kwargs.pop('skip_save', False)
        super().__init__(*args, **kwargs)

        self.cleaned_data = {}

    def is_valid(self):
        if self.skip_save:
            return True
        return super().is_valid()

    def save(self, commit=True, *args, **kwargs):
        if self.skip_save:
            return None
        return super().save(commit=commit, *args, **kwargs)