from django.urls import path
from .consumers import NotificationUpdateConsumer

app_name = 'notification'

websocket_urlpatterns = [
    path('ws/notification_updates/', NotificationUpdateConsumer.as_asgi()),
]
