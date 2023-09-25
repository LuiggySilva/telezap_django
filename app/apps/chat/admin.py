from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Chat, ChatMessage, TextMessage, ImageMessage
from .forms import ChatMessageAdminForm, ChatAdminForm, TextMessageAdminForm, ImageMessageAdminForm, FullChatMessageAdminForm


@admin.register(TextMessage)
class TextMessageAdmin(admin.ModelAdmin):
    search_fields = ('author__email', 'text')
    list_display = ('modify', 'date', 'message_type', 'id')
    fieldsets = (
        ('Mensagem', {
            'fields': ('author', 'text',),
        }),
    )
    readonly_fields = ('author',)

    def modify(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        return format_html(f'<a href="{url}">{obj.author.email}</a>', url)
    modify.short_description = 'Autor'

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.readonly_fields = ()
        else:
            self.readonly_fields = ('author',) 
        return super().get_form(request, obj, **kwargs)

    form = TextMessageAdminForm


@admin.register(ImageMessage)
class ImageMessageAdmin(admin.ModelAdmin):
    search_fields = ('author__email',)
    list_display = ('modify', 'date', 'message_type', 'id')
    fieldsets = (
        ('Mensagem', {
            'fields': ('author', 'image',),
        }),
    )

    def modify(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        return format_html(f'<a href="{url}">{obj.author.email}</a>', url)
    modify.short_description = 'Autor'

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.readonly_fields = ()
        else:
            self.readonly_fields = ('author',) 
        return super().get_form(request, obj, **kwargs)

    form = ImageMessageAdminForm


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    search_fields = ('user1__email', 'user2__email')
    list_display = ('modify', 'user1', 'user1_view', 'user1_exit_chat', 'user2', 'user2_view', 'user2_exit_chat')
    list_filter = ('user1_view', 'user2_view',)
    fieldsets = (
        (
            'Usuário 1', {
                'fields': ('user1', 'user1_view', 'user1_exit_chat_date'),
            },
        ),
        (
          'Usuário 2', {
                'fields': ('user2', 'user2_view', 'user2_exit_chat_date'),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.readonly_fields = ()
        else:
            self.readonly_fields = ('user1', 'user2') 
        return super().get_form(request, obj, **kwargs)

    def user1_exit_chat(self, obj):
        return obj.user1_exit_chat_date is not None
    user1_exit_chat.boolean = True
    user1_exit_chat.short_description = 'Usuário 1 já saiu chat?'

    def user2_exit_chat(self, obj):
        return obj.user2_exit_chat_date is not None
    user2_exit_chat.boolean = True
    user2_exit_chat.short_description = 'Usuário 2 já saiu chat?'

    def modify(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[obj.id])
        return format_html(f'<a href="{url}">Modificar</a>', url)
    modify.short_description = ''

    form = ChatAdminForm


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    search_fields = ('chat__user1__email', 'chat__user2__email')
    list_display = ('chat', 'visualized', 'message', 'message_date', 'id')
    list_filter = ('visualized', 'message__message_type')
    fieldsets = (
        'Mensagem', {
            'fields': ('chat', 'message', 'visualized',),
        },
    ),

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.readonly_fields = ()
        else:
            self.readonly_fields = ('chat', 'message') 
        return super().get_form(request, obj, **kwargs)

    form = ChatMessageAdminForm

    def message_date(self, obj):
        return obj.message.date
    message_date.short_description = 'Data'

    def change_visualized_value_selected(self, request, obj):
        for o in obj.all():
            o.visualized = not o.visualized
            o.save()
    change_visualized_value_selected.short_description = 'Alterar visualização das mensagens selecionadas'

    actions = ['change_visualized_value_selected']


