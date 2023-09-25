from django.urls import path, include
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chats, name='chats'),
    path('<uuid:id>/', views.chat, name='chat'),
    path('<uuid:id>/remove/', views.remove_chat, name='remove_chat'),
    path('<uuid:id>/messages/', views.get_chat_messages, name='get_chat_messages'),
    path('<uuid:id>/message/', views.new_chat_message, name='new_chat_message'),
]