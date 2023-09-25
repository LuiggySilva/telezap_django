
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models import signals
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.base import ContentFile


import os, sys
from pathlib import Path

User = get_user_model()


@receiver(signals.pre_save, sender=User)
def user_slug_pre_save(sender, instance,  **kwargs):
    '''
    Signal to create a slug for the user.
    '''

    instance.slug = slugify(instance.username)


@receiver(signals.pre_save, sender=User)
def user_photo_pre_save(sender, instance, **kwargs):
    '''
    Signal to set a default photo for the user.
    '''

    if not 'test' in sys.argv: # avoid this signal in tests
        default_profile_image_path = Path(settings.MEDIA_ROOT) / 'default_profile_photo.jpg'
        # if the user has a photo
        if instance.photo:
            try:
                # get the old user photo
                old_instance = User.objects.get(pk=instance.pk)
                # if the user photo is different from the old user photo
                if instance.photo != old_instance.photo:
                    # delete the old user photo
                    old_instance.photo.delete(save=False)
                    # set the new user photo
                    old_instance.photo = instance.photo
            except User.DoesNotExist:
                pass
        else:
            # set the default user photo
            with default_profile_image_path.open(mode="rb") as f:
                image_data = f.read()

            image_file = ContentFile(image_data, name=default_profile_image_path.name)
            instance.photo = image_file


@receiver(signals.post_delete, sender=User)
def user_post_delete(sender, instance, **kwargs):
    '''
    Signal to remove the user photo and the user friends when the user is deleted.
    '''

    # remove user photo
    if instance.photo:
        instance.photo.delete(save=False)

    # remove user friends
    instance.friends.clear()


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    '''
    Signal to update the user session id when the user is logged in.
    '''

    User.objects.filter(pk=user.pk).update(session_id=request.session.session_key)


@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):
    '''
    Signal to update the user session id when the user is logged out.
    '''

    User.objects.filter(pk=user.pk).update(session_id=None)