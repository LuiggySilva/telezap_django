from django.apps import AppConfig


class VideocallConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.videocall'

    def ready(self):
        from . import signals