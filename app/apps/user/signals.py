
from django.db.models import signals
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(signals.pre_save, sender=User)
def user_pre_save(sender, instance, **kwargs):
    # update user slug
    instance.slug = slugify(instance.username)

    # update user photo
    try:
        old_instance = User.objects.get(pk=instance.pk)
        if instance.photo != old_instance.photo:
            old_instance.photo.delete(save=False)
            old_instance.photo = instance.photo 
    except User.DoesNotExist:
        pass


@receiver(signals.post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    # remove user photo
    if instance.photo:
        instance.photo.delete(save=False)

    # remove user friends
    instance.friends.clear()