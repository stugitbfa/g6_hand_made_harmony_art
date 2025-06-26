from django.apps import AppConfig


class WebConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.web'

    def ready(self):
        import apps.web.signals

from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps,web'

    def ready(self):
        import apps.web.signals  
