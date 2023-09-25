from django.db.models import Q
from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.utils import dateformat, timezone

from PIL import Image
from io import BytesIO
import base64, json
from apps.chat.templatetags.custom_tags import is_user_attribute_visible
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Chat, ChatMessage, TextMessage, ImageMessage
from apps.utils import date_is_today, get_all_emojis, get_message_separator, get_chat_dict


@login_required
def chats(request):
    '''
    View to list all chats of the user.

    Args:
        request (HttpRequest): The request object.

    Returns:
        render: The render of the template with the chats.

    Context:
        chats (list): A list of dictionaries containing the chat and the another user.
        chat dictionaries:
            - chat (Chat): The chat.
            - another_user (User): The another user in chat.
            - amount_of_messages (int): The amount of messages in the chat.
            - amount_of_unviewed_messages (int): The amount of unviewed messages in the chat.
            - last_message (ChatMessage): The last message of the chat.
            - last_message_date (datetime): The date of the last message of the chat.
            - has_unread_messages (bool): True if the chat has unread messages, False otherwise.
            - last_message_date_is_today (bool): True if the last message date is today, False otherwise.
    '''

    # Get all visible chats of user 
    chats = Chat.objects.filter(
                (Q(user1=request.user) & Q(user1_view=True)) | 
                (Q(user2=request.user) & Q(user2_view=True))
            )

    messages_dicts = []
    # For each chat, create a dictionary with the chat and the another user
    for chat in chats:
        # Get the init_messsages_date
        chat_dict = get_chat_dict(chat, request.user)
        messages_dicts.append(chat_dict)

    context = {
        'chats': messages_dicts
    }
    return render(request, 'chat/chat_list.html', context=context)



@login_required
def get_chat_messages(request, id):
    '''
    View to get the messages of a chat.

    Args:
        request (HttpRequest): The request object.
        id (uuid): The id of the chat.

    Returns:
        JsonResponse: A json response with the messages of the chat.

    Context:
        message_list (list): A list of dictionaries containing the message and the separator.
        message dictionaries:
            - template (str): The template of the message.
            - separator (str): The separator of the message.
            - is_last_unviewed_message (bool): True if the message is the last unviewed message, False otherwise.
    
    Notes:
        - The messages are paginated.
        - The messages are ordered by date.
        - The user can only get the messages of a chat if he is in the chat.
    '''

    if request.method == 'GET':
        # Get the chat and the page of the messages
        chat = get_object_or_404(Chat, id=id)
        page = request.GET.get("page", 1)

        # Check if the user is in the chat
        if not chat.user1 == request.user and not chat.user2 == request.user:
            messages.add_message(request, constants.ERROR, 'Você não tem permissão para receber as mensagens desse chat.')
            return HttpResponseRedirect(reverse('chat:chats'))
        
        messages_per_page = settings.MESSAGES_PAGINATION

        init_messsages_date = None
        # If the user is the user1 and the user1 has exit the chat, set the init_messsages_date to the user1_exit_chat_date
        if chat.user1 == request.user and chat.user1_exit_chat_date:
            init_messsages_date = chat.user1_exit_chat_date
        elif chat.user2 == request.user and chat.user2_exit_chat_date:
            init_messsages_date = chat.user2_exit_chat_date
        # Get the messages of the chat from the init_messsages_date to now
        messages_list = chat.get_messages(init_messsages_date=init_messsages_date)

        # If the chat has no messages, return a json response with no messages
        if messages_list is None:
            return JsonResponse({"message_list":None, "has_next":False})

        # Get the last unviewed message of the chat
        last_unviewed_message = chat.get_first_unviewed_message(request.user)
        last_unviewed_message_index = 0
        # If the user is viewing the first page of the chat, update the messages visualization of the user to visualized
        if int(page) == 1:
            chat.update_messages_visualization(request.user)

        # Create a list of dictionaries with the messages and the separators
        message_data_list = []
        for index in range(len(messages_list)):
            msg = messages_list[index]
            content = dict()

            # If the message is from the user, render the message_send template, otherwise render the message_received template
            if msg.author == request.user:
                # Render the message_send template
                template = render_to_string('chat/message_send.html', {'message': msg})
            else:
                # Check if the user can see the online status and the photo of the message author
                visibility_online = is_user_attribute_visible(
                    request_user=request.user,
                    message_author=msg.author,
                    attribute="online"
                )
                visibility_photo = is_user_attribute_visible(
                    request_user=request.user,
                    message_author=msg.author,
                    attribute="photo"
                )
                # Render the message_received template
                template = render_to_string(
                    'chat/message_received.html', 
                    {
                        'message': msg, 
                        'visibility_online': visibility_online, 
                        'visibility_photo': visibility_photo
                    }
                )

            # Add the template and the separator to the dictionary
            content['template'] = str(template)
            content['separator'] = get_message_separator(msg.date, messages_list[index+1].date) if index < len(messages_list)-1 else None
            
            # If the message is the last unviewed message, set the is_last_unviewed_message to True, otherwise set it to False
            # Serves to highlight the last unviewed message
            if last_unviewed_message is not None and last_unviewed_message == msg.id:
                content['is_last_unviewed_message'] = True
                last_unviewed_message_index = index
            else:
                content['is_last_unviewed_message'] = False

            # Add the dictionary to the list
            message_data_list.append(content)

        # If the last unviewed message is not None and the index of the last unviewed message is greater than the messages per page, set the messages per page to the index of the last unviewed message plus 2
        # Serves to guarantee that the last unviewed message will be in the first page
        if last_unviewed_message is not None and last_unviewed_message_index > messages_per_page:
            messages_per_page = last_unviewed_message_index + 2

        # Paginate the messages
        paginator = Paginator(message_data_list, messages_per_page)
        try:
            # Get the page of the messages
            paginator.validate_number(page)
            messages_list = paginator.get_page(page)

            # Create a list of messages
            paginated_messages = []
            for msg in messages_list:
                paginated_messages.append(msg)

            # Return a json response with the messages and if the messages has next page
            data = {"message_list":paginated_messages, "has_next":messages_list.has_next()}
            return JsonResponse(data)
        except (EmptyPage, PageNotAnInteger):
            # If the page is not valid, return a json response with no messages
            return JsonResponse({"message_list":None, "has_next":False})



@login_required
def chat(request, id):
    '''
    View to show the requested chat.

    Args:
        request (HttpRequest): The request object.
        id (uuid): The id of the chat.

    Returns:
        render: The render of the template with the chat.

    Context:
        - chat (Chat): The chat.
        - another_user (User): The another user in chat.
        - emojis (list): A list of emojis.

    Notes:
        - The chat is only shown if the user is in the chat.
    '''

    # Get the chat
    chat = get_object_or_404(Chat, id=id)

    # Check if the user is in the chat
    if not chat.user1 == request.user and not chat.user2 == request.user:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para acessar este chat.')
        return HttpResponseRedirect(reverse('chat:chats'))
    
    # Update the user chat visualization if the user is in the chat and the user has not viewed the chat
    if chat.user1 == request.user and chat.user1_view == False:
        chat.user1_view = True
        chat.save()
    elif chat.user2 == request.user and chat.user2_view == False:
        chat.user2_view = True
        chat.save()

    # Get the another user in chat
    another_user = chat.get_another_user(request.user)
    context = {
        'chat': chat,
        'another_user': another_user,
        'emojis': get_all_emojis(),
        'another_user_is_friend': request.user.is_friend(another_user)
    }
    return render(request, 'chat/chat.html', context=context)



def is_user_connected_in_chat(user_id, chat_id):
    '''
    Function to check if a user is connected in a chat.

    Args:
        user_id (int): The id of the user.
        chat_id (str|uuid): The id of the chat.
    
    Returns:
        bool: True if the user is connected in the chat, False otherwise.
    '''

    group_name = f'user_{user_id}_chat_{chat_id}'
    channel_layer = get_channel_layer()
    return group_name in channel_layer.groups

@login_required
def new_chat_message(request, id):
    '''
    View to create a new message in a chat.

    Args:
        request (HttpRequest): The request object.
        id (uuid): The id of the chat.

    Returns:
        HttpResponse: A http response with status 204 if the message was created, 404 if the chat was not found or 403 if the user is not in the chat.
    
    Notes:
        - The user can only create a new message in a chat if he is in the chat.
    '''

    # Get the chat
    chat = get_object_or_404(Chat, id=id)
    # Check if the user is in the chat
    if not chat.user1 == request.user and not chat.user2 == request.user:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para enviar mensagens neste chat.')
        return HttpResponseRedirect(reverse('chat:chats'))

    # Get the another user in chat and check if he is connected in the chat
    another_user = chat.get_another_user(request.user)
    another_user_is_connected_in_chat = is_user_connected_in_chat(another_user.id, str(chat.id))
    if request.method == 'POST':
        # Get the message type
        message_type = request.POST.get('message_type')
        match message_type:
            case 'T':
                # If the message type is text, create a new text message and a new chat message with the text message
                message_text = request.POST.get('text')
                text_message = TextMessage.objects.create(
                    author=request.user,
                    text=message_text
                )
                ChatMessage.objects.create(
                    chat=chat,
                    message=text_message,
                    visualized= another_user_is_connected_in_chat
                )
            case 'I':
                # If the message type is image, create a new image message and a new chat message with the image message
                message_image = request.FILES.get('image')
                image_message = ImageMessage.objects.create(
                    author=request.user,
                    image=message_image
                )
                ChatMessage.objects.create(
                    chat=chat,
                    message=image_message,
                    visualized= another_user_is_connected_in_chat
                )
            case 'A':
                # If the message type is audio, create a new text message and a new chat message with the text message
                message_text = 'Áudio'
                text_message = TextMessage.objects.create(
                    author=request.user,
                    text=message_text
                )
                ChatMessage.objects.create(
                    chat=chat,
                    message=text_message,
                    visualized= another_user_is_connected_in_chat
                )
            case 'V':
                # If the message type is video, create a new text message and a new chat message with the text message
                message_text = 'Vídeo'
                text_message = TextMessage.objects.create(
                    author=request.user,
                    text=message_text
                )
                ChatMessage.objects.create(
                    chat=chat,
                    message=text_message,
                    visualized= another_user_is_connected_in_chat
                )
            case _:
                # If the message type is invalid, return a http response with status 404
                messages.add_message(request, constants.ERROR, 'Tipo de mensagem inválido.')
                return HttpResponseRedirect(reverse('chat:chat', kwargs={'id': id}))
        return HttpResponse(status=204)
    return HttpResponse(status=200)


@login_required
def remove_chat(request, id):
    '''
    View to remove a chat.

    Args:
        request (HttpRequest): The request object.
        id (uuid): The id of the chat.

    Returns:
        HttpResponseRedirect: A http response redirect to the chats page.
    
    Notes:
        - The user can only remove a chat if he is in the chat.
    '''

    # Get the chat
    chat = get_object_or_404(Chat, id=id)
    # Check if the user is in the chat
    if not chat.user1 == request.user and not chat.user2 == request.user:
        messages.add_message(request, constants.ERROR, 'Você não tem permissão para remover este chat.')
        return HttpResponseRedirect(reverse('chat:chats'))

    localized_datetime = timezone.localtime(timezone.now(), timezone=timezone.get_current_timezone())

    if chat.user1 == request.user:
        chat.user1_view = False
        chat.user1_exit_chat_date = localized_datetime
        chat.save()
    else:
        chat.user2_view = False
        chat.user2_exit_chat_date = localized_datetime
        chat.save()

    if chat.user1_view == False and chat.user2_view == False:
        chat.delete()

    messages.add_message(request, constants.SUCCESS, 'Chat removido com sucesso.')
    return HttpResponseRedirect(reverse('chat:chats'))
