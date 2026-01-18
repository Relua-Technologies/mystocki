class AlwaysCreateIfNewFormMixin:
    
    def has_changed(self, *args, **kwargs):
        if getattr(self.instance, 'id', None) is None:
            return True
        return super().has_changed(*args, **kwargs)
