from django.urls import path, include
from . import views

app_name = 'notification'

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('reply/', views.reply_notification_request, name='reply_notification_request'),
    path('remove_notifications/', views.remove_notifications_visibility, name='remove_notifications'),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
]