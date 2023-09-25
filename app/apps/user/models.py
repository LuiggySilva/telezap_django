from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, BaseUserManager
from django.db.models import signals
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.sessions.models import Session

import string, emoji, os


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


def validate_text(value):
    if any(char in string.punctuation or emoji.is_emoji(char) for char in value):
        raise ValidationError("O seu nick não pode conter caracteres especiais ou emojis.")


class User(AbstractUser):
    username = models.CharField(max_length=20, verbose_name="Nick", unique=True, validators=[validate_text])
    email = models.EmailField(_('Email'), unique=True)
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    status = models.TextField(max_length=250, blank=True, verbose_name="Status")
    photo = models.ImageField(
        upload_to='user_profiles_photos',
        verbose_name="Foto",
        blank=True,
    )
    friends = models.ManyToManyField('self', blank=True, symmetrical=True, verbose_name='Amigos')

    profile_visibility_types = (
        ('QU', 'Qualquer um'),
        ('AA', 'Apenas amigos'),
        ('NM', 'Ninguém'), 
    )

    config_email_visibility = models.CharField(
        max_length=2, 
        choices=profile_visibility_types, 
        default=profile_visibility_types[0], 
        verbose_name="Visibilidade do email"
    )
    config_status_visibility = models.CharField(
        max_length=2, 
        choices=profile_visibility_types, 
        default=profile_visibility_types[0], 
        verbose_name="Visibilidade do status"
    )
    config_photo_visibility = models.CharField(
        max_length=2, 
        choices=profile_visibility_types, 
        default=profile_visibility_types[0], 
        verbose_name="Visibilidade da foto"
    )
    config_online_visibility = models.CharField(
        max_length=2,
        choices=profile_visibility_types,
        default=profile_visibility_types[0], 
        verbose_name="Visibilidade do online"
    )

    session_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID da sessão")
    in_chat = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Ativo agora no(s) Chat(s)")
    in_groupchat = models.CharField(max_length=1000, blank=True, null=True, verbose_name="Ativo agora no(s) Grupo(s)")

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"


    def is_online(self):
        if Session.objects.filter(session_key=self.session_id).exists():
            return True
        else:
            User.objects.filter(email=self.email).update(session_id=None)
            return False


    def is_friend(self, user):
        return user in self.friends.all()


    def have_pending_notifications(self):
        from apps.utils import user_has_pending_notifications 
        return user_has_pending_notifications(self)


    #TODO: Implementar
    def have_pending_group_messages(self):
        return False


    def user_has_unviewed_chat_messages(self):
        from apps.utils import user_has_unviewed_chat_messages
        return user_has_unviewed_chat_messages(self)