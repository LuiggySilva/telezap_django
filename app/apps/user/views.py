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

from .models import User
from .forms import (
    CustomUserCreationForm, 
    UserProfileForm,
    UserProfileConfigForm
)
from apps.util import get_all_emojis


class LandingPageView(TemplateView):
    """
    View para renderizar a página inicial do site.

    Herda da classe TemplateView que é usada para renderizar um template
    sem qualquer processamento adicional de dados.

    Attributes:
        template_name (str): O nome do template a ser usado para renderizar a página.

    Notes:
        Essa view não requer nenhum dado adicional para ser exibida, pois apenas
        renderiza o template da página inicial do site.
    """

    template_name = 'user/landing_page.html'


class SignupView(CreateView):
    """
    View para o formulário de inscrição de novos usuários.

    Herda da classe CreateView que é usada para renderizar um formulário
    de criação de objetos e salvar novos objetos no banco de dados.

    Attributes:
        template_name (str): O nome do template a ser usado para renderizar a página.
        form_class (Form): A classe do formulário a ser usado para criar novos usuários.

    Methods:
        get_success_url: Sobrescreve o método para redirecionar para a página de login
            após o cadastro bem-sucedido.

    Notes:
        Para o cadastro de novos usuários, o formulário de criação é fornecido
        pela classe CustomUserCreationForm, que foi definida em forms.py.
    """

    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class UserProfileView(LoginRequiredMixin, DetailView):
    """
    View para exibir o perfil do usuário logado.

    Herda da classe DetailView que é usada para exibir detalhes de um objeto,
    neste caso, o objeto User.

    Attributes:
        template_name (str): O nome do template a ser usado para renderizar a view.
        queryset (QuerySet): O conjunto de objetos a partir do qual os detalhes
            são exibidos. Neste caso, todos os usuários são incluídos.
        context_object_name (str): O nome da variável de contexto que contém o
            objeto User que será usado no template.

    Methods:
        get_context_data: Sobrescreve o método para adicionar contextos adicionais
            além do objeto User ao template, como formulários de edição e emojis.
    """

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

        context = super(UserProfileView, self).get_context_data(*args, **kwargs)

        emojis_categories = get_all_emojis()

        context.update(
            {
                'form_perfil': UserProfileForm(instance=self.get_object()),
                'form_config_perfil': UserProfileConfigForm(instance=self.get_object()),
                'form_senha_perfil': PasswordChangeForm(user=self.get_object()),
                'emojis_categories': emojis_categories
            }
        )
        return context


@login_required
def profile_update(request, slug):
    """
    View para atualização do perfil do usuário.

    Essa view é acessível apenas para usuários autenticados.

    Args:
        request (HttpRequest): O objeto HttpRequest contendo os dados da requisição.
        slug (str): O slug do usuário cuja senha será atualizada.

    Returns:
        HttpResponseRedirect: Redireciona para a página do perfil do usuário após a atualização do seu perfil.
    """

    if request.method == "POST":
        # Obtém o usuário autenticado com base no slug do usuário da requisição
        slug = request.user.slug
        user = User.objects.get(slug=slug)
        user_id = user.pk
        # Cria o formulário de alteração do perfil do usuário e os dados enviados pelo formulário POST
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        # Caso o formulário seja válido salva as alterações do perfil no banco de dados
        if (form.is_valid()):
            form.save()
            user = User.objects.get(pk=user_id)
            # Adiciona uma mensagem de sucesso para ser exibida na próxima página
            messages.add_message(request, constants.SUCCESS, 'Perfil atualizado com sucesso!')
        else:
            # Se o formulário não for válido, exibe uma mensagem de erro para cada erro encontrado
            messages.add_message(request, constants.ERROR,'Erro na alteração do perfil!')
            for field_name, errors in form.errors.items():
                for error in errors:
                    if field_name == "status":
                        messages.add_message(request, constants.ERROR, f'Status: {error}')
                    else:
                        messages.add_message(request, constants.ERROR, f'{error}')
        # Redireciona para a página do perfil do usuário após a atualização do seu perfil
        return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":user.slug}))
    # Redireciona para a página do perfil do usuário caso o método da requisição não seja POST
    return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))


@login_required
def profile_config_update(request, slug):
    """
    View para atualização das configurações do perfil do usuário.

    Essa view é acessível apenas para usuários autenticados.

    Args:
        request (HttpRequest): O objeto HttpRequest contendo os dados da requisição.
        slug (str): O slug do usuário cuja senha será atualizada.

    Returns:
        HttpResponseRedirect: Redireciona para a página do perfil do usuário após a atualização das suas configurações.
    """

    if request.method == "POST":
        # Obtém o usuário autenticado com base no slug do usuário da requisição
        slug = request.user.slug
        user = User.objects.get(slug=slug)
        # Cria o formulário com os dados do usuário e os dados enviados pelo formulário POST
        form = UserProfileConfigForm(request.POST, instance=user)
        # Caso o formulário seja válido salva as novas configurações no banco de dados
        if (form.is_valid()):
            form.save()
            # Adiciona uma mensagem de sucesso para ser exibida na próxima página
            messages.add_message(request, constants.SUCCESS, 'Configurações atualizadas com sucesso!')
        else:
            # Se o formulário não for válido, exibe uma mensagem de erro para cada erro encontrado
            messages.add_message(request, constants.ERROR, 'Erro na alteração das configurações!')
            for field_name, errors in form.errors.items():
                for error in errors:
                    messages.add_message(request, constants.ERROR, f'{error}')
        # Redireciona para a página do perfil do usuário após a atualização das suas configurações
        return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))
    # Redireciona para a página do perfil do usuário caso o método da requisição não seja POST
    return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))


@login_required
def profile_password_update(request, slug):
    """
    View para atualização de senha do perfil de usuário.

    Essa view é acessível apenas para usuários autenticados.

    Args:
        request (HttpRequest): O objeto HttpRequest contendo os dados da requisição.
        slug (str): O slug do usuário cuja senha será atualizada.

    Returns:
        HttpResponseRedirect: Redireciona para a página de login após a atualização da senha.
    """
    
    if request.method == "POST":
        # Obtém o usuário autenticado com base no slug do usuário da requisição
        slug = request.user.slug
        user = User.objects.get(slug=slug)
        # Cria o formulário com os dados do usuário e os dados enviados pelo formulário POST
        form = PasswordChangeForm(user, request.POST)
        # Caso o formulário seja válido salva a nova senha no banco de dados
        if (form.is_valid()):
            form.save()
            # Adiciona uma mensagem de sucesso para ser exibida na próxima página
            messages.add_message(request, constants.SUCCESS, 'Senha atualizada com sucesso!')
            # Redireciona para a página de login após a atualização da senha
            return HttpResponseRedirect(reverse("logout"))
        else:
            # Se o formulário não for válido, exibe uma mensagem de erro para cada erro encontrado
            messages.add_message(request, constants.ERROR, 'Erro na alteração da senha!')
            for field_name, errors in form.errors.items():
                for error in errors:
                    messages.add_message(request, constants.ERROR, f'{error}')
            # Redireciona para a página do perfil do usuário em caso de erro
            return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))

    # Redireciona para a página de login caso o método da requisição não seja POST
    return HttpResponseRedirect(reverse("user:profile", kwargs={"slug":slug}))
