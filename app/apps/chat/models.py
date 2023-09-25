from django.db import models
from django.db.models import Case, When, CharField, Value
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

import os, uuid

User = get_user_model()


class Message(models.Model):
    type_choices = (
        ('T', 'Texto'),
        ('I', 'Imagem'),
        ('A', 'Audio'),
        ('V', 'Video'),
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Autor')
    message_type = models.CharField(max_length=1, choices=type_choices, editable=False, verbose_name='Tipo')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Data')

    class Meta:
        verbose_name_plural = "Mensagens"

    @classmethod
    def check_and_remove_empty_folder(cls, chat_id):
        media_root_path = os.path.join(settings.MEDIA_ROOT, 'user_chat_media')
        media_folders = [f'images'] # f'audios', f'videos'
        for folder in media_folders:
            folder_path = os.path.join(media_root_path, folder)
            if os.path.exists(folder_path):
                files = os.listdir(folder_path)
                if not files:
                    os.rmdir(folder_path)

    def __str__(self):
        return f'{self.id} - {self.author.email} - {self.get_message_type_display()}'



class TextMessage(Message):
    text = models.TextField(blank=False, null=False, verbose_name='Texto')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_type = 'T'

    class Meta:
        verbose_name = "Mensagem de Texto"
        verbose_name_plural = "Mensagens de Texto"



class ImageMessage(Message):
    image = models.ImageField(upload_to=f'user_chat_media/images/', blank=False, null=False, verbose_name='Imagem')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_type = 'I'

    class Meta:
        verbose_name = "Mensagem de Imagem"
        verbose_name_plural = "Mensagens de Imagem"



class ChatMessage(models.Model):
    chat = models.ForeignKey('Chat', on_delete=models.CASCADE, verbose_name='Chat')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name='Mensagem')
    visualized = models.BooleanField(default=False, verbose_name='Visualizada')

    class Meta:
        verbose_name = "Mensagem de Chat"
        verbose_name_plural = "Mensagens de Chats"
        unique_together = ('chat', 'message')

    def __str__(self):
        return f'{self.message.author.email} - ({self.message.get_message_type_display()}) -> {self.chat}'

    def is_author(self, user):
        return self.message.author == user

    def get_message(self):
        if self.message.message_type == 'T':
            return self.message.textmessage
        elif self.message.message_type == 'I':
            return self.message.imagemessage
        elif self.message.message_type == 'A':
            return None
        elif self.message.message_type == 'V':
            return None
        else:
            return None



class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user1_chats', verbose_name='Usuário 1')
    user2 = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user2_chats', verbose_name='Usuário 2')

    user1_view = models.BooleanField(default=True, verbose_name='Visualização do usuário 1')
    user2_view = models.BooleanField(default=True, verbose_name='Visualização do usuário 2')
    user1_exit_chat_date = models.DateTimeField(blank=True, null=True, verbose_name='Última data de remoção do chat do usuário 1')
    user2_exit_chat_date = models.DateTimeField(blank=True, null=True, verbose_name='Última data de remoção do chat do usuário 2')

    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f'{self.user1.email} - {self.user2.email}'


    def _annotate_queryset(self, queryset):
        annotated_queryset = queryset.annotate(
            message_type=Case(
                When(message__textmessage__isnull=False, then=Value('T')),
                When(message__imagemessage__isnull=False, then=Value('I')),
                default=Value(''),
                output_field=CharField(),
            )
        )
        return annotated_queryset


    def get_another_user(self, user):
        if self.user1 == user:
            return self.user2
        elif self.user2 == user:
            return self.user1
        else:
            raise ValidationError('O usuário não pertence ao chat.')

    
    def update_messages_visualization(self, user):
        if self.user1 == user or self.user2 == user:
            ChatMessage.objects.filter(chat=self, visualized=False).exclude(message__author=user).update(visualized=True)
        else:
            raise ValidationError('O usuário não pertence ao chat.')

    def get_messages(self, init_messsages_date=None):
        messages = ChatMessage.objects.filter(
            chat=self
        ).order_by('-message__date')
        if init_messsages_date:
            messages = messages.exclude(message__date__lt=init_messsages_date)

        if messages.exists():
            annotated_messages = self._annotate_queryset(messages)
            aux = []
            for msg in annotated_messages:
                if msg.message_type == 'T':
                    aux.append(msg.message.textmessage)
                elif msg.message_type == 'I':
                    aux.append(msg.message.imagemessage)
                elif msg.message_type == 'A':
                    pass
                elif msg.message_type == 'V':
                    pass
                else:
                    pass
            return aux
        return None


    def get_last_message(self, date=False, init_messsages_date=None):
        if self.get_amount_of_messages(init_messsages_date=init_messsages_date) == 0:
            return None
        
        if init_messsages_date:
            message_id, message_type, message_date = ChatMessage.objects.filter(
                chat=self
            ).exclude(message__date__lt=init_messsages_date).values_list('message__id', 'message__message_type', 'message__date').last()
        else:
            message_id, message_type, message_date = ChatMessage.objects.filter(
                chat=self
            ).values_list('message__id', 'message__message_type', 'message__date').last()
        
        
        
        match message_type:
            case 'T':
                message = TextMessage.objects.select_related('author').get(id=message_id)
            case 'I':
                message = ImageMessage.objects.select_related('author').get(id=message_id)
            case 'A':
                message = None
            case 'V':
                message = None
            case _:
                message = None

        if date:
            return message, message_date
        else:
            return message


    def get_first_unviewed_message(self, user):
        try:
            message_id, message_type, message_date = ChatMessage.objects.filter(
                chat=self, 
                visualized=False
            ).exclude(message__author=user).values_list(
                'message__id', 'message__message_type', 'message__date'
            ).first()
            return message_id
        except:
            return None


    def have_unviewed_message(self, user):
        return ChatMessage.objects.filter(chat=self, visualized=False).exclude(message__author=user).exists()


    def get_amount_of_unviewed_messages(self, user, init_messsages_date=None):
        if init_messsages_date:
            return ChatMessage.objects.filter(chat=self, visualized=False).exclude(message__author=user).exclude(message__date__lt=init_messsages_date).count()
        else:
            return ChatMessage.objects.filter(chat=self, visualized=False).exclude(message__author=user).count()


    def get_amount_of_messages(self, init_messsages_date=None):
        if init_messsages_date:
            return ChatMessage.objects.filter(chat=self).exclude(message__date__lt=init_messsages_date).count()
        else:
            return ChatMessage.objects.filter(chat=self).count()