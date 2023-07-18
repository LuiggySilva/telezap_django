from django.contrib import admin
from .models import User
from .forms import UserAdminForm

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm

    list_display = ('email', 'username', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')

    filter_horizontal = ['friends', ]

    fieldsets = (
        ('Perfil', {
            'fields': ('username', 'slug', 'email', 'password', 'status', 'photo', 'friends'),
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
                'user_permissions',
                'groups',
            ),
            'classes': ('collapse',),
        })
    )