from django.test import TestCase
from .factories import UserFactory, User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.db import transaction

class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()


    def test_str_method(self):
        '''
        Description:
            Tests the __str__ method of the User model.

        Preconditions:
            - The User model must be defined correctly.

        Postconditions:
            - The __str__ method must return the user's username.
        '''
        
        username = 'testuser'
        self.user = UserFactory(username=username)
        self.assertEqual(str(self.user), username)


    def test_username_validator(self):
        '''
        Description:
            Tests the username validator of the User model.

        Preconditions:
            - None.

        Postconditions:
            - The validator must raise a ValidationError exception if the username contains special characters or emojis.
        '''

        with self.assertRaises(ValidationError):
            user_with_special_chars = UserFactory(username='my_user!')
            user_with_special_chars.full_clean()

        with self.assertRaises(ValidationError):
            user_with_emoji = UserFactory(username='my😊username')
            user_with_emoji.full_clean()

    
    def test_username_max_length_validator(self):
        '''
        Description:
            Tests the max length validator of the User model's username field.

        Preconditions:
            - None.

        Postconditions:
            - The validator must raise a ValidationError exception if the username has more than 20 characters.
        '''
        
        with self.assertRaises(ValidationError):
            user_with_long_username = UserFactory(username='mylongusername' * 5)
            user_with_long_username.full_clean()


    def test_status_max_length_validator(self):
        '''
        Description:
            Tests the max length validator of the User model's status field.

        Preconditions:
            - None.

        Postconditions:
            - The validator must raise a ValidationError exception if the status has more than 250 characters.
        '''
        
        with self.assertRaises(ValidationError):
            user_with_long_status = UserFactory(status='mylongstatus' * 50)
            user_with_long_status.full_clean()


    def test_unique_username(self):
        '''
        Description:
            Tests the uniqueness of the User model's username.

        Preconditions:
            - Another user with the same username as the user to be created must not exist.

        Postconditions:
            - The User model must raise an IntegrityError exception if the username already exists.
            - The user must not be created.
        '''

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                user1 = UserFactory(username='myuser')

                user2 = UserFactory(username='myuser')

        self.assertEqual(User.objects.count(), 1)


    def test_unique_email(self):
        '''
        Description:
            Tests the uniqueness of the User model's email.

        Preconditions:
            - Another user with the same email as the user to be created must not exist.

        Postconditions: 
            - The User model must raise an IntegrityError exception if the email already exists.
            - The user must not be created.
        '''

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                user1 = UserFactory(username='myuser1', email='myuser@email.com')

                user2 = UserFactory(username='myuser2', email='myuser@email.com')

        self.assertEqual(User.objects.count(), 1)


    def test_slug_field(self):
        '''
        Description:
            Tests the slug field of the User model.

        Preconditions:
            - The User model must be defined correctly.

        Postconditions:
            - The slug field must be created automatically from the user's username.
        '''

        username = 'Test User Slug'
        self.user = UserFactory(username=username)
        self.assertEqual(self.user.slug, 'test-user-slug')


    def test_default_visibility_fields_values(self):
        '''
        Description:
            Tests the default visibility fields of the User model.

        Preconditions:
            - The User model must be defined correctly.

        Postconditions:
            - The default visibility fields must be defined correctly.
        '''

        user = UserFactory(username='myuser')
        self.assertEqual(user.config_email_visibility, ('QU', 'Qualquer um'))
        self.assertEqual(user.config_status_visibility, ('QU', 'Qualquer um'))
        self.assertEqual(user.config_photo_visibility, ('QU', 'Qualquer um'))


    def test_fields_choices(self):
        '''
        Description:
            Tests the choices of the User model's visibility fields.

        Preconditions:
            - The User model must be defined correctly.

        Postconditions:
            - The choices of the visibility fields must be defined correctly.
        '''

        user = UserFactory(username='myuser')
        self.assertEqual(user.profile_visibility_types, (
            ('QU', 'Qualquer um'),
            ('AA', 'Apenas amigos'),
            ('NM', 'Ninguém'), 
        ))
    
