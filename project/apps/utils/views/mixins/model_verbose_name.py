class ModelVerboseNameViewMixin:
    verbose_name_model = None

    def get_verbose_name(self):
        if self.verbose_name_model:
            return self.verbose_name_model._meta.verbose_name
        return None

    def get_verbose_name_plural(self):
        if self.verbose_name_model:
            return self.verbose_name_model._meta.verbose_name_plural
        return None
