from django.urls import path
from .consumers import ChatConsumer, ChatsConsumer

app_name = 'chat'

websocket_urlpatterns = [
    path('ws/chats/', ChatsConsumer.as_asgi()),
    path('ws/chat/<uuid:chat_id>/', ChatConsumer.as_asgi()),
]
