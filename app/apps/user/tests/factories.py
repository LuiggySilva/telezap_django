from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import File

import factory, tempfile, os

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}email@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')
    status = factory.Faker('text', max_nb_chars=250)
    #photo = factory.django.ImageField()