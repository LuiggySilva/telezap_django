from django.contrib import admin
from .models import User
from .forms import UserAdminForm

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

    list_display = ('email', 'username', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login', 'slug', 'session_id', 'in_chat', 'in_groupchat')

    filter_horizontal = ['friends',]

    fieldsets = (
        ('Perfil', {
            'fields': ('slug', 'username', 'email', 'password', 'status', 'photo', 'friends', 'session_id', 'in_chat', 'in_groupchat'),
        }),
        ('Configurações: Quem pode ver os dados pessoais', {
            'fields': (
                'config_email_visibility', 
                'config_status_visibility',
                'config_photo_visibility',
                'config_online_visibility',
            ),
        }),
        ('Atributos do Django',{
            'fields': (
                'first_name',
                'last_name',
                'is_staff',
                'is_active',
                'is_superuser',
                'date_joined',
                'last_login',
                'user_permissions',
                'groups',
            ),
            'classes': ('collapse',),
        })
    )