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

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.readonly_fields = ()
        else:
            self.readonly_fields = ('author', 'receiver', 'group') 
        return super().get_form(request, obj, **kwargs)


@admin.register(GroupRequest)
class GroupRequestAdmin(admin.ModelAdmin):
    form = GroupRequestAdminForm
    list_display = ('author', 'receiver', 'group', 'status', 'date', 'author_view', 'receiver_view')
    search_fields = ('author', 'receiver', 'group')
    list_filter = ('status',)
    form = GroupRequestAdminForm

    fieldsets = (
        ('Solicitação', {
            'fields': ('author','author_view', 'receiver', 'receiver_view', 'group', 'status',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            self.readonly_fields = ()
        else:
            self.readonly_fields = ('author', 'receiver', 'group') 
        return super().get_form(request, obj, **kwargs)
    