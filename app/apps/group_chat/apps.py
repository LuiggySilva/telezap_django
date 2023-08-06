from django.apps import AppConfig


class GroupChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.group_chat'
    verbose_name = 'Chat em grupo'

    def ready(self):
        from . import signals