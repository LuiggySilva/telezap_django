from django.apps import AppConfig


class VideocallConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.videocall'
    verbose_name = 'Video Chamada'

    def ready(self):
        from . import signals