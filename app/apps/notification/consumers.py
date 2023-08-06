import json
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import FriendshipRequest, GroupRequest
from .serializers import FriendshipRequestSerializer, GroupRequestSerializer
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationUpdateConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']

        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}_notifications"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()


    async def disconnect(self, close_code):
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def send_notification_update(self, event):
        if hasattr(self, 'user') and self.user.is_authenticated:
            notification_id = event['notification_id']
            notification_type = event['notification_type']

            notification_types = {
                "FriendshipRequest": {
                    "notification": await sync_to_async(FriendshipRequest.objects.get)(id=notification_id),
                },
                "GroupRequest": {
                    "notification": await sync_to_async(GroupRequest.objects.get)(id=notification_id),
                },
            }

            notification = notification_types[notification_type]['notification']
            group_id = None if notification_type == "FriendshipRequest" else notification.group.id

            request_user_is_autor = await sync_to_async(notification.is_author)(self.user)
            if request_user_is_autor:
                await self.send(text_data=json.dumps({
                    'id': notification.id,
                    'group_id': group_id,
                    'status': notification.get_status_display(),
                    'finished': notification.is_finished(),
                    'type':'update'
                }))


    async def send_notification_create(self, event):
        if hasattr(self, 'user') and self.user.is_authenticated:
            notification_id = event['notification_id']
            notification_type = event['notification_type']

            notification_types = {
                "FriendshipRequest": {
                    "notification": await self.get_FriendshipRequest(notification_id),
                    "serializer": FriendshipRequestSerializer,
                    "is_group": False,
                },
                "GroupRequest": {
                    "notification": await self.get_GroupRequest(notification_id),
                    "serializer": GroupRequestSerializer,
                    "is_group": True,
                },
            }
            notification = notification_types[notification_type]['notification']
            serializer = notification_types[notification_type]['serializer'](notification)
            is_group = notification_types[notification_type]['is_group']

            request_user_is_author = await sync_to_async(notification.is_author)(self.user)
            templates = {
                True : {
                    "template": render_to_string('notification/notification_send.html', {'notification': notification, 'is_group':is_group}),
                    "is_sent": True,
                },
                False : {
                    "template": render_to_string('notification/notification_received.html', {'notification': notification, 'is_group':is_group}),
                    "is_sent": False,
                }
            }
            template = templates[request_user_is_author]['template']
            is_sent = templates[request_user_is_author]['is_sent']

            await self.send(text_data=json.dumps({
                'type': 'new',
                'notification': serializer.data,
                'template': template,
                'is_group': is_group,
                'is_sent': is_sent,
            }))

    
    @database_sync_to_async
    def get_FriendshipRequest(self, id):
        qs = FriendshipRequest.objects.filter(id=id)
        if qs.exists():
            obj = qs.select_related('author','receiver').get(id=id)
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_GroupRequest(self, id):
        qs = GroupRequest.objects.filter(id=id)
        if qs.exists():
            obj = qs.select_related('author','receiver').get(id=id)
        else:
            obj = None
        return obj