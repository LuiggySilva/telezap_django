from emoji_data_python import emoji_data
from django.db.models import Q, Subquery, OuterRef
from django.core.files import File
from django.conf import settings

from apps.chat.models import ChatMessage, Chat
from apps.notification.models import FriendshipRequest, GroupRequest

from datetime import datetime, timedelta
import os, json
from pathlib import Path


def get_all_emojis():
    '''
    Function to get all emojis

    Returns:
        list: A list of all emojis
    '''

    emojis_file_path = Path(settings.MEDIA_ROOT) / 'emojis.json'
    with emojis_file_path.open(mode="r") as f:
        emojis_categories = json.load(f)

    return emojis_categories


def user_has_pending_notifications(user):
    '''
    Function to check if the user has pending notifications

    Parameters:
        user (User): The user to be checked

    Returns:
        bool: True if the user has pending notifications, False otherwise
    '''

    return FriendshipRequest.objects.filter(receiver=user, status='P').exists() or GroupRequest.objects.filter(receiver=user, status='P').exists()


def user_has_unviewed_chat_messages(user):
    '''
    Function to check if the user has unviewed chat messages

    Parameters:
        user (User): The user to be checked

    Returns:
        bool: True if the user has unviewed chat messages, False otherwise
    '''

    # get all user chats where the user is the user1 and user1_view is True or the user is the user2 and user2_view is True
    all_user_chats = Chat.objects.filter(
        (Q(user1=user) & Q(user1_view=True)) |
        (Q(user2=user) & Q(user2_view=True))
    )

    # if the user is in a chat, exclude the chat from the query
    if user.in_chat:
        all_user_chats = all_user_chats.exclude(pk__in=user.in_chat.split('|'))

    # get all chat messages where the chat is in the all_user_chats query and the message author is not the user
    subquery = ChatMessage.objects.filter(
        chat=OuterRef('pk'),
        visualized=False,
    ).exclude(
        message__author=user
    ).values('chat')

    # return True if the query returns any result, False otherwise
    return all_user_chats.filter(
        pk__in=Subquery(subquery)
    ).exists()


def date_is_today(date):
    '''
    Function to check if the date is today

    Parameters:
        date (datetime): The date to be checked

    Returns:
        bool: True if the date is today, False otherwise
    '''

    return date.date() == datetime.now().date()


def date_is_yesterday(date):
    '''
    Function to check if the date is yesterday

    Parameters:
        date (datetime): The date to be checked

    Returns:
        bool: True if the date is yesterday, False otherwise
    '''

    return date.date() == datetime.now().date() - timedelta(days=1)


def get_message_separator(message_date, previous_message_date):
    '''
    Function to get the message separator (date) in the chat

    Parameters:
        message_date (datetime): The date of the message
        previous_message_date (datetime): The date of the previous message

    Returns:
        str: The date separator
    '''

    # if the message date is the same as the previous message date, return None
    if message_date.date() == previous_message_date.date():
        return None
    else:
        if date_is_today(message_date):
            # if the message date is today, return 'Hoje'
            return 'Hoje'
        elif date_is_yesterday(message_date):
            # if the message date is yesterday, return 'Ontem'
            return 'Ontem'
        else:
            # if the message date is not today or yesterday, return the date in the format 'dd/mm/yyyy'
            return message_date.strftime('%d/%m/%Y')


def get_chat_dict(chat, user):
    '''
    Function to get a chat dict
    '''

    if user == chat.user1 and chat.user1_exit_chat_date:
        init_messsages_date = chat.user1_exit_chat_date
    elif user == chat.user2 and chat.user2_exit_chat_date:
        init_messsages_date = chat.user2_exit_chat_date
    else:
        init_messsages_date = None

    chat_dict = dict()
    chat_dict['chat'] = chat
    chat_dict['another_user'] = chat.get_another_user(user)
    amount_of_messages = chat.get_amount_of_messages(init_messsages_date=init_messsages_date)
    chat_dict['amount_of_messages'] = amount_of_messages
    amount_of_unviewed_messages = chat.get_amount_of_unviewed_messages(user)
    chat_dict['amount_of_unviewed_messages'] = amount_of_unviewed_messages
    # If the chat has messages, get the last message and its date
    if amount_of_messages > 0:
        last_message, last_message_date = chat.get_last_message(date=True) 
        chat_dict['last_message'] = last_message
        chat_dict['last_message_date'] = last_message_date
        chat_dict['has_unread_messages'] = chat.have_unviewed_message(user)
        chat_dict['last_message_date_is_today'] = date_is_today(last_message_date)
    else: # If the chat has no messages, set the last message and its date to None
        chat_dict['last_message'] = None
        chat_dict['last_message_date'] = None
        chat_dict['has_unread_messages'] = False
        chat_dict['last_message_date_is_today'] = False

    return chat_dict