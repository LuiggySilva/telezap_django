"""
ASGI config for telezap_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.notification.routing import websocket_urlpatterns as notification_websocket_urlpatterns
from apps.chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
# TODO: from apps.group_chat.routing import websocket_urlpatterns as group_chat_websocket_urlpatterns
# TODO: from apps.videocall.routing import websocket_urlpatterns as videocall_websocket_urlpatterns
from telezap_django.routing import websocket_urlpatterns as navbar_websocket_urlpatterns 

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telezap_django.settings')


application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket': AuthMiddlewareStack(
        URLRouter(
            notification_websocket_urlpatterns + 
            chat_websocket_urlpatterns + 
            navbar_websocket_urlpatterns
        )
    ),
})