from django.db.models import signals
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ImageMessage, TextMessage, Chat, ChatMessage


@receiver(signals.post_delete, sender=ImageMessage)
def image_message_post_delete(sender, instance, **kwargs):
    '''
    Signal to delete image file when ImageMessage is deleted
    '''

    if instance.image:
        instance.image.delete(save=False)


@receiver(signals.post_save, sender=ImageMessage)
def image_message_post_update(sender, instance, **kwargs):
    '''
    Signal to delete old image file when ImageMessage is updated
    '''

    if(not kwargs['created']):
        try:
            old_instance = ImageMessage.objects.get(pk=instance.pk)
            if instance.image != old_instance.image:
                old_instance.image.delete(save=False)
                old_instance.image = instance.image 
        except ImageMessage.DoesNotExist:
            pass


@receiver(signals.post_save, sender=ChatMessage)
def chat_message_post_save(sender, instance, **kwargs):
    '''
    Signal to send message to chat
    '''

    channel_layer = get_channel_layer()
    send_type = "send_message_create"

    user1 = instance.message.author
    user2 = instance.chat.get_another_user(user1)
    if instance.chat.user1 == user1:
        new_chat_user1 = not instance.chat.user1_view
        new_chat_user2 = not instance.chat.user2_view
    else:
        new_chat_user1 = not instance.chat.user2_view
        new_chat_user2 = not instance.chat.user1_view
    

    # Send message to user1 chat list
    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{user1.id}_messages", 
        {
            "type": send_type, 
            "chat_id": str(instance.chat.id),
            "chat_message_id": instance.message.id,
            "chat_message_author": instance.message.author.username,
            "chat_message_type": instance.message.message_type,
            "chat_unviewed_messages_count": instance.chat.get_amount_of_unviewed_messages(user1),
            "chat_message_date": instance.message.date,
            "new_chat": new_chat_user1,
        }
    )
    # Send message to user1 chat
    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{user1.id}_chat_{str(instance.chat.id)}", 
        {
            "type": send_type,
            "chat_id": str(instance.chat.id),
            "chat_message_id": instance.message.id,
            "chat_message_type": instance.message.message_type,
            "chat_message_is_author": instance.is_author(user1),
        }
    )


    # Send message to user2 chat list
    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{user2.id}_messages", 
        {
            "type": send_type, 
            "chat_id": str(instance.chat.id),
            "chat_message_id": instance.message.id,
            "chat_message_author": instance.message.author.username,
            "chat_message_type": instance.message.message_type,
            "chat_unviewed_messages_count": instance.chat.get_amount_of_unviewed_messages(user2),
            "chat_message_date": instance.message.date,
            "new_chat": new_chat_user2,
        }
    )
    # Send message to user2 chat
    async_to_sync(
        channel_layer.group_send
    )(
        f"user_{user2.id}_chat_{str(instance.chat.id)}", 
        {
            "type": send_type,
            "chat_id": str(instance.chat.id),
            "chat_message_id": instance.message.id,
            "chat_message_type": instance.message.message_type,
            "chat_message_is_author": instance.is_author(user2),
        }
    )


    if instance.chat.user1 == user1 and instance.chat.user2_view == False:
        instance.chat.user2_view = True
        instance.chat.save()
    elif instance.chat.user2 == user1 and instance.chat.user1_view == False:
        instance.chat.user1_view = True
        instance.chat.save()


    has_unviewed_messages = ChatMessage.objects.filter(chat=instance.chat, visualized=False).exists()

    # Send message to user1 navbar
    if instance.chat.user1_view:
        async_to_sync(
            channel_layer.group_send
        )(
            f"user_{user1.id}_navbar", 
            {
                "type": "navbar_chat_unviewed_messages",
                "value": has_unviewed_messages,
            }
        )
    # Send message to user2 navbar
    if instance.chat.user2_view:
        async_to_sync(
            channel_layer.group_send
        )(
            f"user_{user2.id}_navbar", 
            {
                "type": "navbar_chat_unviewed_messages",
                "value": has_unviewed_messages,
            }
        )