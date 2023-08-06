from django.contrib import admin
from .models import FriendshipRequest, GroupRequest
from .forms import FriendshipRequestAdminForm, GroupRequestAdminForm

@admin.register(FriendshipRequest)
class FriendshipRequestAdmin(admin.ModelAdmin):
    form = FriendshipRequestAdminForm
    list_display = ('author', 'receiver', 'status', 'date', 'author_view', 'receiver_view')
    search_fields = ('author', 'receiver')
    list_filter = ('status',)
    form = FriendshipRequestAdminForm

@admin.register(GroupRequest)
class GroupRequestAdmin(admin.ModelAdmin):
    form = GroupRequestAdminForm
    list_display = ('author', 'receiver', 'group', 'status', 'date', 'author_view', 'receiver_view')
    search_fields = ('author', 'receiver', 'group')
    list_filter = ('status',)
    form = GroupRequestAdminForm
    