from django.contrib.auth.tokens import default_token_generator
from django import template
from django.db.models import Q

from emoji import is_emoji

from apps.utils import date_is_today as date_is_today_util
from apps.chat.models import Chat

register = template.Library()

@register.filter(name='date_is_today')
def date_is_today(date):
    '''
    Filter that checks if the date is today.
    '''

    return date_is_today_util(date)


@register.filter(name='emoji_not_italic', is_safe=True)
def emoji_not_italic(text):
    new_string = ""
    for char in text: 
        #is_emoji = bool(re.match(r'\p{RGI_Emoji}', char, re.UNICODE))  # Verificar se é um emoji Unicode
        if is_emoji(char):
            new_string += f'<span class="no-italic">{char}</span>'
        else:
            new_string += char
    return new_string


@register.filter(name='get_chat_id')
def get_chat_id(user1, user2):
    '''
    Filter that gets the chat id between two users.
    '''
    chat_id = Chat.objects.get(
        Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
    ).id

    return str(chat_id)


@register.filter(name='is_user_friend')
def is_user_friend(user_request, message_author):
    '''
    Filter that checks if the user is a friend of the message author.
    '''
    
    return user_request in message_author.friends.all()


@register.simple_tag(name='is_user_attribute_visible')
def is_user_attribute_visible(**kwargs):
    '''
    Simple tag that checks if the user attribute is visible to the user.
    '''

    user_request = kwargs['request_user']
    message_author = kwargs['message_author']
    attribute = kwargs['attribute']
    
    is_friend = user_request in message_author.friends.all()

    if len(message_author.config_online_visibility.split("'")) > 1:
        config_online_visibility = message_author.config_online_visibility.split("'")[1]
        config_status_visibility = message_author.config_status_visibility.split("'")[1]
        config_email_visibility = message_author.config_email_visibility.split("'")[1]
        config_photo_visibility = message_author.config_photo_visibility.split("'")[1]
    else:
        config_online_visibility = message_author.config_online_visibility
        config_status_visibility = message_author.config_status_visibility
        config_email_visibility = message_author.config_email_visibility
        config_photo_visibility = message_author.config_photo_visibility

    user_request_attributes = {
        'online': (config_online_visibility, is_friend, message_author.is_online()),
        'status': (config_status_visibility, is_friend),
        'email':  (config_email_visibility, is_friend),
        'photo':  (config_photo_visibility, is_friend),
    }

    user_attributes_visibility = {
        'online': {
            ('QU', True, True): 'online-status',
            ('QU', True, False): 'offline-status',
            ('QU', False, True): 'online-status',
            ('QU', False, False): 'offline-status',

            ('AA', True, True) : 'online-status',
            ('AA', True, False) : 'offline-status',
            ('AA', False, True) : 'nobody-status',
            ('AA', False, False) : 'nobody-status',

            ('NM', True, True): 'nobody-status',
            ('NM', True, False): 'nobody-status',
            ('NM', False, True): 'nobody-status',
            ('NM', False, False): 'nobody-status',
        },
        'status': {
            ('QU', True): True,
            ('QU', False): True,
            ('AA', True) : True,
            ('AA', False) : False,
            ('NM', True): False,
            ('NM', False): False,
        },
        'email': {
            ('QU', True): True,
            ('QU', False): True,
            ('AA', True) : True,
            ('AA', False) : False,
            ('NM', True): False,
            ('NM', False): False,
        },
        'photo': {
            ('QU', True): True,
            ('QU', False): True,
            ('AA', True) : True,
            ('AA', False) : False,
            ('NM', True): False,
            ('NM', False): False,
        },
    }
    
    return user_attributes_visibility[attribute][user_request_attributes[attribute]]
        