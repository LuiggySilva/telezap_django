
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import (
    TemplateView, 
    ListView, 
    DetailView, 
    DeleteView, 
    UpdateView, 
    CreateView, 
    FormView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth import get_user_model

from .models import FriendshipRequest, GroupRequest
from apps.chat.models import Chat
import json

User = get_user_model()


@login_required
def notifications(request):
    '''
    View to render the user's notifications page.

    Args:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        render: Render the user's notifications page.

    Context:
        - friend_requests_sent:
            List of friendship requests sent by the logged in user.
        - friend_requests_received:
            List of friendship requests received by the logged in user.
        - group_requests_sent:
            List of group requests sent by the logged in user.
        - group_requests_received:
            List of group requests received by the logged in user.

    Notes:
        - If the method is POST the view will search for a user with the email passed in the search form.
        - If the method is POST and the user is found, the user will be added to the context.
        - If the method is GET the view will render the notifications page.
    '''

    '''
        self.META = {
            "REQUEST_METHOD": self.method,
            "QUERY_STRING": query_string,
            "SCRIPT_NAME": self.script_name,
            "PATH_INFO": self.path_info,
            # WSGI-expecting code will need these for a while
            "wsgi.multithread": True,
            "wsgi.multiprocess": True,
        }
    '''

    # Get friend requests sent by the user with your visualization as True ordered by date
    friend_requests_sent = FriendshipRequest.objects.filter(
        author=request.user, 
        author_view=True
    ).order_by('-date')
    # Get friend requests received by the user with your visualization as True ordered by date
    friend_requests_received = FriendshipRequest.objects.filter(
        receiver=request.user, 
        receiver_view=True
    ).order_by('-date')
    # Get group requests sent by the user with your visualization as True ordered by date
    group_requests_sent = GroupRequest.objects.filter(
        author=request.user, 
        author_view=True
    ).order_by('-date')
    # Get group requests received by the user with your visualization as True ordered by date
    group_requests_received = GroupRequest.objects.filter(
        receiver=request.user, 
        receiver_view=True
    ).order_by('-date')
    
    context = {
        'friend_requests_sent': friend_requests_sent,
        'friend_requests_received': friend_requests_received,
        'group_requests_sent': group_requests_sent,
        'group_requests_received': group_requests_received,
    }

    if request.method == "POST":
        # Verify if the user exists
        if User.objects.filter(email=request.POST.get("email")).exists():
            user_search_result = User.objects.get(email=request.POST.get("email"))
            # Verify if the user is the logged in user
            if request.user == user_search_result:
                messages.add_message(request, constants.ERROR, 'Você não pode se adicionar como amigo.')
                return render(request, "notification/notifications.html", context=context)
            # Return the user search result
            context['user_search_result'] = user_search_result
            return render(request, "notification/notifications.html",context=context)
        else:
            # Return an error message if the user is not found
            messages.add_message(request, constants.ERROR, 'Nenhum usuário com esse email foi encontrado.')
            return render(request, "notification/notifications.html", context=context)
    else:
        # Render the notifications page if the method is not POST
        return render(request, "notification/notifications.html", context=context)



@login_required
def reply_notification_request(request):
    '''
    View to reply to a friendship or group request.

    Args:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponseRedirect: Redirect the user to the notifications page.

    Notes:
        - If the method is POST the view will search for the friendship or group request with the id passed.
        - If the method is POST and the request is found, the request will be answered.
        - If the method is POST and the request is answered successfully, the user will be redirected to the notifications page.
        - If the method is POST and the request is not found, an error message will be added to the context and the user will be redirected to the notifications page.
        - If the method is POST and the user does not have permission to respond to the request, an error message will be added to the context and the user will be redirected to the notifications page.
        - If the method is GET the user will be redirected to the notifications page.
    '''
    
    if request.method == "POST":
        # Get the notification id and type
        notification_id = request.POST.get("notification_id")
        notification_type = request.POST.get("notification_type")
        try:
            # Verify type of notification
            if notification_type == "A":
                # Get the friend request notification with the id passed
                notification = FriendshipRequest.objects.get(id=notification_id)
            else:
                # Get the group request notification with the id passed
                notification = GroupRequest.objects.get(id=notification_id)
        except (FriendshipRequest.DoesNotExist, GroupRequest.DoesNotExist):
            # Return an error message if the notification is not found
            messages.add_message(request, constants.ERROR, 'Notificação não encontrada.')
            return HttpResponseRedirect(reverse("notification:notifications"))

        # Verify if the user has permission to respond to the request
        if request.user == notification.receiver:
            # Verify if the user accepted the request
            if bool(request.POST.get("reply")):
                # Update the notification status to accepted
                notification.status = "A"
                # Add the users as friends
                notification.author.friends.add(notification.receiver)
                notification.receiver.friends.add(notification.author)
                # Update the notification visualization to False
                notification.receiver_view = False
                notification.save()
                # Create a chat between the users
                if (not Chat.objects.filter(
                        Q(user1=notification.author, user2=notification.receiver) | Q(user1=notification.receiver, user2=notification.author)
                   ).exists()):
                    Chat.objects.create(user1=notification.author, user2=notification.receiver)
                # Add a success message to the context
                if notification_type == "A":
                    messages.add_message(request, constants.SUCCESS, f'{notification.author} agora é seu amigo(a)!')
                else:
                    messages.add_message(request, constants.SUCCESS, f'Você agora é membro do grupo {notification.group}!')
            else:
                # Update the notification status to refused
                notification.status = "R"
                notification.save()
            # Return the user to the notifications page
            return HttpResponseRedirect(reverse("notification:notifications"))
        else:
            # Return an error message if the user does not have permission to respond to the request
            messages.add_message(request, constants.ERROR, 'Você não tem permissão para realizar essa ação.')
            return HttpResponseRedirect(reverse("notification:notifications"))

    # Return the user to the notifications page if the method is not POST
    return HttpResponseRedirect(reverse("notification:notifications"))


@login_required
def remove_notifications_visibility(request):
    '''
    View to remove the visibility of friendship and group notifications from a user.

    Args:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponseRedirect: Redirect the user to the notifications page.

    Notes:
        - If the method is POST the view will remove the visibility of friendship or group notifications from the user.
        - If the method is POST and the visibility is successfully removed, the user will be redirected to the notifications page.
        - If the method is GET the user will be redirected to the notifications page.
    '''
    
    if request.method == "POST":
        # Get the type of notification
        notification_type = request.POST.get("notification_type")
        # Verify the type of notification
        if notification_type == "A":
            # Update the visibility of friendship notifications from the user to False
            friend_requests = FriendshipRequest.objects.filter(author=request.user).exclude(status='P')
            for friend_request in friend_requests:
                friend_request.author_view = False
                friend_request.save()
            friend_requests = FriendshipRequest.objects.filter(receiver=request.user).exclude(status='P')
            for friend_request in friend_requests:
                friend_request.receiver_view = False
                friend_request.save()
            messages.add_message(request, constants.SUCCESS, 'Notificações de amizade finalizadas removidas.')
        else:
            # Update the visibility of group notifications from the user to False
            group_requests = GroupRequest.objects.filter(author=request.user).exclude(status='P')
            for group_request in group_requests:
                group_request.author_view = False
                group_request.save()
            group_requests = GroupRequest.objects.filter(receiver=request.user).exclude(status='P')
            for group_request in group_requests:
                group_request.receiver_view = False
                group_request.save()
            messages.add_message(request, constants.SUCCESS, 'Notificações de grupo finalizadas removidas.')
        return HttpResponseRedirect(reverse("notification:notifications"))

    # Return the user to the notifications page if the method is not POST
    return HttpResponseRedirect(reverse("notification:notifications"))


@login_required
def send_friend_request(request):
    '''
    View to send a friend request.

    Args:
        request (HttpRequest): The request object used to generate this response.

    Returns:
        HttpResponseRedirect: Redirect the user to the notifications page.

    Notes:
        - If the method is POST the view will search for a user with the email passed.
        - If the method is POST and the user is already a friend of the logged in user, a warning message will be added to the context and the user will be redirected to the notifications page.
        - If the method is POST and the user has already sent a friend request to the logged in user, a warning message will be added to the context and the user will be redirected to the notifications page.
        - If the method is POST and the user is found, the friend request will be sent.
        - If the method is POST and the user is found, the user will be redirected to the notifications page.
        - If the method is GET the user will be redirected to the notifications page.
    '''
    
    if request.method == "POST":
        try:
            # Get the user with the email passed
            error_var = ''
            if 'email' in request.POST:
                error_var = 'email'
                user = User.objects.get(email=request.POST.get("email"))
            elif 'slug' in request.POST:
                error_var = 'slug'
                user = User.objects.get(slug=request.POST.get("slug"))

        except User.DoesNotExist:
            # Return an error message if the user is not found
            messages.add_message(request, constants.ERROR, f"Nenhum usuário(a) com esse {error_var} foi encontrado.")
            return HttpResponseRedirect(reverse("notification:notifications"))
        
        # Verify if the user is the logged in user
        if request.user == user:
            # Return an error message if the user self-adds as a friend
            messages.add_message(request, constants.WARNING, "Você não pode se adicionar como amigo.")
            return HttpResponseRedirect(reverse("notification:notifications"))
        elif request.user.friends.filter(id=user.id).exists():
            # Return an error message if the user is already a friend of the logged in user
            messages.add_message(request, constants.WARNING, "Você já é amigo desse usuário(a).")
            return HttpResponseRedirect(reverse("notification:notifications"))
        elif FriendshipRequest.objects.filter(author=request.user, receiver=user, status="P").exists():
            # Return an error message if the user has already sent a friend request to the logged in user
            messages.add_message(request, constants.WARNING, "Você já enviou uma solicitação de amizade para esse usuário(a).")
            return HttpResponseRedirect(reverse("notification:notifications"))
        else:
            # Create a friend request notification
            FriendshipRequest.objects.create(author=request.user, receiver=user, status="P")
            messages.add_message(request, constants.SUCCESS, f"Solicitação de amizade enviada para '{user.email}' com sucesso!")
            return HttpResponseRedirect(reverse("notification:notifications"))

    # Return the user to the notifications page if the method is not POST
    return HttpResponseRedirect(reverse("notification:notifications"))