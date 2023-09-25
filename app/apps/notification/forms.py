from django import forms
from .models import FriendshipRequest, GroupRequest, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class FriendshipRequestForm(forms.ModelForm):
    class Meta:
        model = FriendshipRequest
        fields = ['author', 'receiver']

    
class GroupRequestForm(forms.ModelForm):
    class Meta:
        model = GroupRequest
        fields = ['author', 'receiver']


class NotificationAdminForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        author = cleaned_data.get("author")
        receiver = cleaned_data.get("receiver")
        id = cleaned_data.get("id")
        if GroupRequest.objects.filter(id=id, author=author, receiver=receiver).exists():
            self.add_error("author", "Não é possível criar uma notificação com author e receiver iguais.")
            self.add_error("receiver", "Não é possível criar uma notificação com author e receiver iguais.")

        return cleaned_data


class FriendshipRequestAdminForm(NotificationAdminForm):
    class Meta(NotificationAdminForm.Meta):
        model = FriendshipRequest
        labels = {
            'author': 'Autor',
            'receiver': 'Recebedor',
            'author_view': 'Visualização do Autor',
            'receiver_view': 'Visualização do Recebedor',
            'status': 'Status',
            'notification_type': 'Tipo',
        }

    def clean(self):
        cleaned_data = super().clean()
        author = cleaned_data.get("author")
        receiver = cleaned_data.get("receiver")
        id = cleaned_data.get("id")

        if FriendshipRequest.objects.filter(id=id, author=author, receiver=receiver).exists():
            self.add_error("author", "Uma solicitação de amizade já foi enviada para esse usuário.")
            self.add_error("receiver", "Uma solicitação de amizade já foi enviada para esse usuário.")

        return cleaned_data


class GroupRequestAdminForm(NotificationAdminForm):
    class Meta(NotificationAdminForm.Meta):
        model = GroupRequest
        labels = {
            'author': 'Autor',
            'receiver': 'Recebedor',
            'author_view': 'Visualização do Autor',
            'receiver_view': 'Visualização do Recebedor',
            'status': 'Status',
            'notification_type': 'Tipo',
            'group': 'Grupo'
        }

    def clean(self):
        cleaned_data = super().clean()
        author = cleaned_data.get("author")
        receiver = cleaned_data.get("receiver")
        id = cleaned_data.get("id")

        if GroupRequest.objects.filter(id=id, author=author, receiver=receiver).exists():
            self.add_error("author", "Uma solicitação de grupo já foi enviada para esse usuário.")
            self.add_error("receiver", "Uma solicitação de grupo já foi enviada para esse usuário.")

        return cleaned_data