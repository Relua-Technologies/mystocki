from django.apps import AppConfig

APP_NAME = 'core'

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = f'apps.{APP_NAME}'

    def ready(self):
        import apps.core.receivers