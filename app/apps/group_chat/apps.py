from django.apps import AppConfig


class GroupChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.group_chat'

    def ready(self):
        from . import signals