from django.urls import path
from .consumers import NavBarConsumer

app_name = 'navbar'

websocket_urlpatterns = [
    path('ws/navbar/', NavBarConsumer.as_asgi()),
]
