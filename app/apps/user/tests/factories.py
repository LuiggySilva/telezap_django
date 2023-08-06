import factory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile, os

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpassword')

    status = factory.Faker('text', max_nb_chars=250)
    photo = factory.django.ImageField()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        '''
            Overwrites the _create method of the base class so that the profile image is created and
            deleted after the user is created.
        '''

        photo_field = model_class._meta.get_field('photo')

        if 'photo' in kwargs and kwargs['photo'] is not None:
            photo = kwargs.pop('photo')
            if isinstance(photo, str):
                temp_image_path = tempfile.NamedTemporaryFile(suffix='.jpg').name
                with open(temp_image_path, 'wb') as temp_image:
                    temp_image.write(photo.encode())
                kwargs['photo'] = SimpleUploadedFile(name='user_profile_photos/default.png', content=open(temp_image_path, 'rb').read(), content_type='image/png')
                os.remove(temp_image_path)

        return super()._create(model_class, *args, **kwargs)