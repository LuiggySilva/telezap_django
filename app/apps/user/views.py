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
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404


from .models import User
from .forms import (
    CustomUserCreationForm, 
    UserProfileForm,
    UserProfileConfigForm
)
from apps.util import get_all_emojis
from apps.notification.models import FriendshipRequest, GroupRequest


class LandingPageView(TemplateView):
    '''
    View to render the site's landing page.

    Inherits from the TemplateView class which is used to render a template
    without any additional data processing.

    Attributes:
        template_name (str): The name of the template to be used to render the page.

    Notes:
        This view does not require any additional data to be displayed, as it only
        renders the site's landing page template.
    '''

    template_name = 'user/landing_page.html'


class SignupView(CreateView):
    '''
    View for the new user signup form.

    Inherits from the CreateView class which is used to render a form
    for creating objects and saving new objects to the database.

    Attributes:
        template_name (str): The name of the template to be used to render the page.
        form_class (Form): The form class to be used for creating new users.

    Methods:
        get_success_url: Overrides the method to redirect to the login page
            after successful signup.

    Notes:
        For the signup of new users, the creation form is provided
        by the CustomUserCreationForm class, which was defined in forms.py.
    '''

    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class UserProfileView(LoginRequiredMixin, DetailView):
    '''
    View to display the logged in user's profile.

    Inherits from the DetailView class which is used to display details of an object,
    in this case, the User object.

    Attributes:
        template_name (str): The name of the template to be used to render the page.
        queryset (QuerySet): The set of objects from which the details are displayed.
            In this case, all users are included.
        context_object_name (str): The name of the context variable that contains the
            User object that will be used in the template.

    Methods:
        get_context_data: Overrides the method to add additional contexts in addition
            to the User object to the template, such as editing forms and emojis.

    Notes:
        This view is only accessible to authenticated users.
    '''

    template_name = "user/profile.html"
    queryset = User.objects.all()
    context_object_name = "user"

    def get_context_data(self, *args, **kwargs):
        """
        Adiciona contextos adicionais ao template.

        Este método é chamado para obter o dicionário de contexto que será passado
        ao template. Aqui, estamos adicionando os seguintes contextos adicionais:
        - form_perfil: Um formulário para edição do perfil do usuário.
        - form_config_perfil: Um formulário para edição das configuraçôes do perfil do usuário.
        - form_senha_perfil: Um formulário para alteração de senha do usuário.
        - emojis_categories: Um dicionário contendo emojis agrupados por categoria.

        Returns:
            dict: Dicionário contendo os contextos adicionais.
        """
        '''
        Adds additional contexts to the template.

        This method is called to get the context dictionary that will be passed
        to the template. Here, we are adding the following additional contexts:
        - form_user_profile: A form for editing the user's profile.
        - form_user_profile_config: A form for editing the user's profile settings.
        - form_user_profile_password: A form for changing the user's password.
        - emojis: A dictionary containing emojis grouped by category. 
        '''

        context = super(UserProfileView, self).get_context_data(*args, **kwargs)

        emojis_categories = get_all_emojis()

        context.update(
            {
                'form_user_profile': UserProfileForm(instance=self.get_object()),
                'form_user_profile_config': UserProfileConfigForm(instance=self.get_object()),
                'form_user_profile_password': PasswordChangeForm(user=self.get_object()),
                'emojis': emojis_categories
            }
        )
        return context


@login_required
def profile_update(request, slug):
    '''
    View for updating the user's profile.

    Args:
        request (HttpRequest): The HttpRequest object containing the request data.
        slug (str): The slug of the user whose password will be updated.

    Returns:
        HttpResponseRedirect: Redirects to the user's profile page after updating their profile.

    Notes:
        This view is only accessible to authenticated users.
    '''

    if request.method == "POST":
        # Get the authenticated user based on the request user's slug
        slug = request.user.slug
        user = User.objects.get(slug=slug)
        user_id = user.pk
        # Creates the user profile change form and the data sent by the POST form
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        # If the form is valid, save the profile changes to the database
        if (form.is_valid()):
            form.save()
            user = User.objects.get(pk=user_id)
            # Add a success message to be displayed on the next page
            messages.add_message(request, constants.SUCCESS, 'Perfil atualizado com sucesso!')
        else:
            # If the form is not valid, display an error message for each error found
            messages.add_message(request, constants.ERROR,'Erro na alteração do perfil!')
            for field_name, errors in form.errors.items():
                for error in errors:
                    if field_name == "status":
                        messages.add_message(request, constants.ERROR, f'Status: {error}')
                    else:
                        messages.add_message(request, constants.ERROR, f'{error}')
        # Redirects to the user's profile page after updating their profile
        return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":user.slug}))

    # Redirects to the user's profile page if the request method is not POST
    return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))


@login_required
def profile_config_update(request, slug):
    '''
    View for updating the user's profile settings.

    Args:
        request (HttpRequest): The HttpRequest object containing the request data.
        slug (str): The slug of the user whose password will be updated.

    Returns:
        HttpResponseRedirect: Redirects to the user's profile page after updating their profile settings.

    Notes:
        This view is only accessible to authenticated users.
    '''

    if request.method == "POST":
        # Get the authenticated user based on the request user's slug
        slug = request.user.slug
        user = User.objects.get(slug=slug)
        # Creates the form with the user's data and the data sent by the POST form
        form = UserProfileConfigForm(request.POST, instance=user)
        # If the form is valid, save the new settings to the database
        if (form.is_valid()):
            form.save()
            # Add a success message to be displayed on the next page
            messages.add_message(request, constants.SUCCESS, 'Configurações atualizadas com sucesso!')
        else:
            # If the form is not valid, display an error message for each error found
            messages.add_message(request, constants.ERROR, 'Erro na alteração das configurações!')
            for field_name, errors in form.errors.items():
                for error in errors:
                    messages.add_message(request, constants.ERROR, f'{error}')
        # Redirects to the user's profile page after updating their profile settings
        return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))

    # Redirects to the user's profile page if the request method is not POST
    return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))


@login_required
def profile_password_update(request, slug):
    '''
    View for updating the user's password.

    Args:
        request (HttpRequest): The HttpRequest object containing the request data.
        slug (str): The slug of the user whose password will be updated.

    Returns:
        HttpResponseRedirect: Redirects to the login page after updating the password.

    Notes:
        This view is only accessible to authenticated users.
    '''
    
    if request.method == "POST":
        # Get the authenticated user based on the request user's slug
        slug = request.user.slug
        user = User.objects.get(slug=slug)
        # Creates the form with the user's data and the data sent by the POST form
        form = PasswordChangeForm(user, request.POST)
        # If the form is valid, save the new password to the database
        if (form.is_valid()):
            form.save()
            # Add a success message to be displayed on the next page
            messages.add_message(request, constants.SUCCESS, 'Senha atualizada com sucesso!')
            # Redirects to the login page after updating the password
            return HttpResponseRedirect(reverse("logout"))
        else:
            # If the form is not valid, display an error message for each error found
            messages.add_message(request, constants.ERROR, 'Erro na alteração da senha!')
            for field_name, errors in form.errors.items():
                for error in errors:
                    messages.add_message(request, constants.ERROR, f'{error}')
            # Redirects to the user's profile page if the request method is not POST
            return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))

    # Redirects to the login page if the request method is not POST
    return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))


@login_required
def remove_friend(request):
    '''
    View for removing a user from the user's friends list.

    Args:
        request (HttpRequest): The HttpRequest object containing the request data.

    Returns:
        HttpResponseRedirect: Redirects to the user's notifications page after removing the friend.

    Notes:
        This view is only accessible to authenticated users.
    '''

    if request.method == "POST":
        # Get the user to be removed from the POST data
        try:
            user_id = request.POST.get("user_id")
            user = User.objects.get(id=user_id)
            # Remove the user from the user's friends list
            request.user.amigos.remove(user)
            user.amigos.remove(request.user)
            # Add a success message to be displayed on the next page
            messages.add_message(request, constants.SUCCESS, f'"{user}" removido(a) da sua lista de amigos.')
        except User.DoesNotExist:
            # If the user does not exist, add an error message to be displayed on the next page
            messages.add_message(request, constants.ERROR, 'Usuário não encontrado.')
            # Redirects to the user's profile page after removing the friend
            return HttpResponseRedirect(reverse("user:profile"))
    
    # Redirects to the user's profile page if the request method is not POST
    return HttpResponseRedirect(reverse("user:profile"))