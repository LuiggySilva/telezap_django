from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.template.defaultfilters import truncatechars
from django.utils import dateformat, timezone

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json

from apps.chat.templatetags.custom_tags import is_user_attribute_visible
from apps.utils import date_is_today, date_is_yesterday, get_chat_dict
from .models import Chat, ChatMessage, TextMessage, ImageMessage

User = get_user_model()


@database_sync_to_async
def get_TextMessage(id):
    '''
    Function to get a text message from the database
    '''

    qs = TextMessage.objects.filter(id=id)
    if qs.exists():
        obj = qs.select_related('author').get(id=id)
    else:
        obj = None
    return obj


@database_sync_to_async
def get_ImageMessage(id):
    '''
    Function to get an image message from the database
    '''

    qs = ImageMessage.objects.filter(id=id)
    if qs.exists():
        obj = qs.select_related('author').get(id=id)
    else:
        obj = None
    return obj


@database_sync_to_async
def set_UserInChat(user, chat_id):
    '''
    Function to set the user in chat
    '''

    user_in_chat = ''
    if user.in_chat:
        # if the user is already in a chat, add the chat id to the user in chat
        if f"{chat_id}|" in user.in_chat or f"|{chat_id}|" in user.in_chat:
            pass
        elif f"|{chat_id}" in user.in_chat:
            pass
        else:
            # if the user is not in the chat, add the chat id to the user in chat
            user_in_chat = f"{user.in_chat}|{chat_id}"
    else:
        # if the user is not in a chat, set the chat id to the user in chat
        user_in_chat = f"{chat_id}"

    # update the user in chat
    User.objects.filter(id=user.id).update(in_chat=user_in_chat)


@database_sync_to_async
def set_UserOutChat(user, chat_id):
    '''
    Function to set the user out chat
    '''

    user_in_chat = ''
    if user.in_chat:
        # if the user is in a chat, remove the chat id from the user in chat
        if f"{chat_id}|" in user.in_chat or f"|{chat_id}|" in user.in_chat:
            user_in_chat = user.in_chat.replace(f"{chat_id}|", '')
        elif f"|{chat_id}" in user.in_chat:
            user_in_chat = user.in_chat.replace(f"|{chat_id}", '')
        else:
            user_in_chat = user.in_chat.replace(f"{chat_id}", '')

    # update the user in chat
    if user_in_chat == '':
        # if the user is not in a chat, set the user in chat to None
        User.objects.filter(id=user.id).update(in_chat=None)
    else:
        # if the user is in a chat, update the user in chat
        User.objects.filter(id=user.id).update(in_chat=user_in_chat)


@database_sync_to_async
def get_AnotherUserChatAttributeVisibility(request_user, message_author, attribute):
    '''
    Function to get the visibility of any user attribute to another user
    '''

    return is_user_attribute_visible(
        request_user=request_user, 
        message_author=message_author, 
        attribute=attribute
    )


@database_sync_to_async
def get_ChatDict(chat, user):
    '''
    Function to get a chat dict
    '''

    return get_chat_dict(chat, user)


@database_sync_to_async
def get_Chat(id):
    '''
    Function to get a chat from the database
    '''

    qs = Chat.objects.filter(id=id)
    if qs.exists():
        obj = qs.select_related('user1', 'user2').get(id=id)
    else:
        obj = None
    return obj



class ChatsConsumer(AsyncWebsocketConsumer):
    '''
    Consumer to send messages to user chat list
    '''

    async def connect(self):
        self.user = self.scope['user']
        # if the user is authenticated, add the user to the group and accept the connection
        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}_messages"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()


    async def disconnect(self, close_code):
        # if the user is authenticated, remove the user from the group
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)


    async def send_message_create(self, event):
        # if the user is authenticated, send the message to the user chat list
        if hasattr(self, 'user') and self.user.is_authenticated:
            chat_id = event['chat_id']
            chat_message_author = event['chat_message_author']
            chat_message_type = event['chat_message_type']
            chat_unviewed_messages_count = event['chat_unviewed_messages_count']
            chat_message_date = event['chat_message_date']
            chat_message_id = event['chat_message_id']
            new_chat = event['new_chat']
            chat = await get_Chat(chat_id)

            # if the message date is today, format the date to 'H:i', otherwise format the date to 'd/m/Y'
            if date_is_today(chat_message_date):
                localized_datetime = timezone.localtime(chat_message_date, timezone=timezone.get_current_timezone())
                chat_message_date = dateformat.format(localized_datetime, 'H:i')
            else:
                chat_message_date = dateformat.format(chat_message_date, 'd/m/Y')

            match chat_message_type:
                case 'T':
                    # If the message is a text message, get the message text and truncate it to 50 characters
                    chat_message = await get_TextMessage(chat_message_id)
                    chat_message = truncatechars(chat_message.text, 50)
                case 'I':
                    # If the message is an image message, set the message text to 'Foto'
                    chat_message = 'Foto'
                case 'V':
                    # If the message is a video message, set the message text to 'Video'
                    chat_message = 'Video'
                case 'A':
                    # If the message is an audio message, set the message text to 'Audio'
                    chat_message = 'Audio'

            template = None
            if new_chat:
                online_visibility = await get_AnotherUserChatAttributeVisibility(
                    request_user=self.user,
                    message_author=chat.get_another_user(self.user),
                    attribute="online"
                )
                photo_visibility = await get_AnotherUserChatAttributeVisibility(
                    request_user=self.user,
                    message_author=chat.get_another_user(self.user),
                    attribute="photo"
                )
                chat_dict = await get_ChatDict(chat, self.user)

                template = render_to_string(
                    'chat/chat_list_partial.html', 
                    {'chat_dict': chat_dict, 'online_visibility': online_visibility, 'photo_visibility': photo_visibility}
                )

            # send the message to the user chat list
            await self.send(text_data=json.dumps({
                'chat_id': chat_id,
                'chat_message_content': chat_message,
                'chat_message_date': chat_message_date,
                'chat_unviewed_messages_count': chat_unviewed_messages_count,
                'chat_message_author': chat_message_author,
                'type': 'create' if new_chat else 'update',
                'template': template
            }))



class ChatConsumer(AsyncWebsocketConsumer):
    '''
    Consumer to send messages to user chat
    '''

    async def connect(self):
        self.user = self.scope['user']
        # if the user is authenticated, add the user to the group and accept the connection
        if self.user and self.user.is_authenticated:
            self.chat_id = self.scope['url_route']['kwargs']['chat_id']
            self.chat = await get_Chat(self.chat_id)
            self.group_name = f'user_{self.user.id}_chat_{self.chat_id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            # set the user in chat
            await set_UserInChat(self.user, str(self.chat_id))
            await self.accept()
        else:
            await self.close()


    async def disconnect(self, close_code):
        # if the user is authenticated, remove the user from the group and set the user out chat
        if hasattr(self, 'user') and self.user and self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            # set the user out chat
            await set_UserOutChat(self.user, str(self.chat_id))


    async def send_message_create(self, event):
        if hasattr(self, 'user') and self.user.is_authenticated:
            chat_id = event['chat_id']
            chat_message_id = event['chat_message_id']
            chat_message_type = event['chat_message_type']
            chat_message_is_author = event['chat_message_is_author']

            match chat_message_type:
                case 'T':
                    # If the message is a text message, get the message
                    chat_message = await get_TextMessage(chat_message_id)
                case 'I':
                    # If the message is an image message, get the message
                    chat_message = await get_ImageMessage(chat_message_id)
                case 'V':
                    # If the message is a video message, get the message
                    chat_message = None
                case 'A':
                    # If the message is an audio message, get the message
                    chat_message = None

            template = None
            # if the message is from the user, render the message send template, otherwise render the message received template
            if chat_message_is_author:
                template = render_to_string('chat/message_send.html', {'message': chat_message})
            else:
                # get the visibility of the user attribute 'online' of the message author
                visibility = await get_AnotherUserChatAttributeVisibility(
                    request_user=self.user,
                    message_author=self.chat.get_another_user(self.user),
                    attribute="online"
                )
                template = render_to_string('chat/message_received.html', {'message': chat_message, 'visibility':visibility})

            # send the message to the user chat
            await self.send(text_data=json.dumps({
                'chat_id': chat_id,
                'chat_message_id': chat_message_id,
                'chat_message_type': chat_message_type,
                'chat_message_is_author': chat_message_is_author,
                'template': template,
                'type':'create'
            }))