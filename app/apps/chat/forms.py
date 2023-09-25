from django import forms
from django.contrib.auth import get_user_model

from .models import Message, Chat, ChatMessage, TextMessage, ImageMessage

User = get_user_model()


class ChatMessageAdminForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = '__all__'
        labels = {
            'chat': 'Chat',
            'message': 'Mensagem',
            'visualized': 'Visualizada',
            'date': 'Data',
        }

    def clean(self):
        cleaned_data = super().clean()
        
        chat = cleaned_data.get("chat")
        author = cleaned_data.get("message").author
        if not chat.user1 == author and not chat.user2 == author:
            self.add_error("message", "O autor da mensagem não pertence ao chat.")

        return cleaned_data


class ChatAdminForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = '__all__'
        labels = {
            'user1': 'Usuário 1',
            'user2': 'Usuário 2',
            'user1_view': 'Visualização do Usuário 1',
            'user2_view': 'Visualização do Usuário 2',
        }

    def clean(self):
        cleaned_data = super().clean()
        
        user1 = cleaned_data.get("user1", None)
        user2 = cleaned_data.get("user2", None)
        if user1 is None or user2 is None:
            user1 = self.instance.user1
            user2 = self.instance.user2
        
        if user1 == user2:
            self.add_error("user1", "Os usuários devem ser diferentes.")
            self.add_error("user2", "Os usuários devem ser diferentes.")

        return cleaned_data


class TextMessageAdminForm(forms.ModelForm):
    class Meta:
        model = TextMessage
        fields = '__all__'
        labels = {
            'author': 'Autor',
            'text': 'Texto',
        }


class ImageMessageAdminForm(forms.ModelForm):
    class Meta:
        model = ImageMessage
        fields = '__all__'
        labels = {
            'author': 'Autor',
            'image': 'Imagem',
        }


class FullChatMessageAdminForm(forms.ModelForm):
    message_type = forms.ChoiceField(
        label='Tipo de Mensagem',
        choices=[
            ('T', 'Texto'),
            ('I', 'Imagem'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'radio'}),
    )
    text_message = forms.CharField(
        label='Texto',
        widget=forms.Textarea(attrs={'class': 'textarea'}),
        required=False,
    )
    image_message = forms.ImageField(
        label='Imagem',
        required=False,
    )
    author = forms.ModelChoiceField(
        label='Autor',
        queryset=User.objects.all(),
    )

    class Meta:
        model = ChatMessage
        fields = ['chat', 'author', 'message_type', 'text_message', 'image_message']

    def clean(self):
        cleaned_data = super().clean()

        message_type = cleaned_data.get('message_type')
        if message_type == 'text' and not cleaned_data.get('text_message'):
            raise forms.ValidationError('Este campo é obrigatório.')
        elif message_type == 'image' and not cleaned_data.get('image_message'):
            raise forms.ValidationError('Este campo é obrigatório.')

        message_author = cleaned_data.get('author')
        if message_author != cleaned_data.get('chat').user1 and message_author != cleaned_data.get('chat').user2:
            raise forms.ValidationError('O autor da mensagem não pertence ao chat.')

        return cleaned_data
    