from django.db.models.signals import post_save
from django.db.models import signals
from django.dispatch import receiver

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import FriendshipRequest, GroupRequest

@receiver(post_save, sender=FriendshipRequest)
def friendship_request_updated(sender, instance, **kwargs):

    if instance.author_view == False and instance.receiver_view == False:
        instance.delete()
    else:
        channel_layer = get_channel_layer()
        if(kwargs['created']):
            send_type = "send_notification_create"
        else:
            send_type = "send_notification_update"

        async_to_sync(
            channel_layer.group_send
        )(
            f"user_{instance.author.id}_notifications",
            {
                "type": send_type, 
                "notification_id": instance.id,
                "notification_type": "FriendshipRequest", 
                "author_id": instance.author.id, 
                "receiver_id": instance.receiver.id, 
            }
        )

        async_to_sync(
            channel_layer.group_send
        )(
            f"user_{instance.receiver.id}_notifications",
            {
                "type": send_type, 
                "notification_id": instance.id,
                "notification_type": "FriendshipRequest", 
                "author_id": instance.author.id, 
                "receiver_id": instance.receiver.id, 
            }
        )


@receiver(post_save, sender=GroupRequest)
def group_request_updated(sender, instance, **kwargs):
    if instance.author_view == False and instance.receiver_view == False:
        instance.delete()
    else:
        channel_layer = get_channel_layer()
        if(kwargs['created']):
            send_type = "send_notification_create"
        else:
            send_type = "send_notification_update"

        async_to_sync(
            channel_layer.group_send
        )(
            f"user_{instance.author.id}_notifications", 
            {
                "type": send_type, 
                "notification_id": instance.id,
                "notification_type": "GroupRequest", 
                "author_id": instance.author.id, 
                "receiver_id": instance.receiver.id, 
            }
        )

        async_to_sync(
            channel_layer.group_send
        )(
            f"user_{instance.receiver.id}_notifications", 
            {
                "type": send_type, 
                "notification_id": instance.id,
                "notification_type": "GroupRequest", 
                "author_id": instance.author.id, 
                "receiver_id": instance.receiver.id, 
            }
        )
