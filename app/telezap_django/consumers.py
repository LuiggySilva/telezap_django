from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from asgiref.sync import sync_to_async
import json

User = get_user_model()

class NavBarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        # if the user is authenticated, add the user to the group and accept the connection
        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}_navbar"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # if the user is authenticated, remove the user from the group
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def navbar_chat_unviewed_messages(self, event):
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                'type': 'navbar_chat_unviewed_messages',
                'value': event['value']
            }))


    async def navbar_notification_pending_notifications(self, event):
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                'type': 'navbar_notification_pending_notifications',
                'value': event['value']
            }))


    async def navbar_groupchat_unviewed_messages(self, event):
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.send(text_data=json.dumps({
                'type': 'navbar_groupchat_unviewed_messages',
                'value': event['value']
            }))