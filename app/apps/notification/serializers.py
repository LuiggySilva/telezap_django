from rest_framework import serializers
from .models import Notification, FriendshipRequest, GroupRequest


class NotificationSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'author_view', 'receiver_view', 'date', 'status', 'status_display']

    def get_status_display(self, obj):
        return obj.get_status_display()


class FriendshipRequestSerializer(NotificationSerializer):
    class Meta(NotificationSerializer.Meta):
        model = FriendshipRequest


class GroupRequestSerializer(NotificationSerializer):
    class Meta(NotificationSerializer.Meta):
        model = GroupRequest
