from django.test import TestCase
from .factories import UserFactory
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()


    def test_user_model_str_method(self):
        '''
        Descrição:
            Testa o método __str__ do modelo User.

        Pré-condições:
            - O modelo User deve estar definido corretamente.

        Pós-condições:
            - O método __str__ deve retornar o username do usuário.
        '''
        
        username = 'testuser'
        self.user = UserFactory(username=username)
        self.assertEqual(str(self.user), username)


    def test_user_model_username_validator(self):
        '''
        Descrição:
            Testa o validador de username do modelo User.

        Pré-condições:
            - Nenhuma.

        Pós-condições:
            - O validador deve levantar uma exceção ValidationError caso o username contenha caracteres especiais ou emojis.
            - O usuário não deve ser criado.
        '''
        
        with self.assertRaises(ValidationError):
            user_with_special_chars = UserFactory(username='my_user!')
            user_with_special_chars.full_clean()

        with self.assertRaises(ValidationError):
            user_with_emoji = UserFactory(username='my😊username')
            user_with_emoji.full_clean()

    
    def test_user_model_username_max_length_validator(self):
        '''
        Descrição:
            Testa o validador de tamanho máximo do username do modelo User.

        Pré-condições:
            - Nenhuma.

        Pós-condições:
            - O validador deve levantar uma exceção ValidationError caso o username tenha mais de 20 caracteres.
            - O usuário não deve ser criado.
        '''
        
        with self.assertRaises(ValidationError):
            user_with_long_username = UserFactory(username='mylongusername' * 5)
            user_with_long_username.full_clean()


    def test_user_model_status_max_length_validator(self):
        '''
        Descrição:
            Testa o validador de tamanho máximo do status do modelo User.

        Pré-condições:
            - Nenhuma.

        Pós-condições:
            - O validador deve levantar uma exceção ValidationError caso o status tenha mais de 250 caracteres.
            - O usuário não deve ser criado.
        '''
        
        with self.assertRaises(ValidationError):
            user_with_long_status = UserFactory(status='mylongstatus' * 50)
            user_with_long_status.full_clean()


    def test_user_model_unique_username(self):
        '''
        Descrição:
            Testa a unicidade do username do modelo User.

        Pré-condições:
            - Outro usuário com o username igual ao do usuário a ser criado não deve existir.

        Pós-condições:
            - O modelo User deve levantar uma exceção IntegrityError caso o username já exista.
            - O usuário não deve ser criado.
        '''

        with self.assertRaises(IntegrityError):
            user1 = UserFactory(username='myuser')

            user2 = UserFactory(username='myuser')


    def test_user_model_unique_email(self):
        '''
        Descrição:
            Testa a unicidade do email do modelo User.

        Pré-condições:
            - Outro usuário com o email igual ao do usuário a ser criado não deve existir.

        Pós-condições:
            - O modelo User deve levantar uma exceção IntegrityError caso o email já exista.
            - O usuário não deve ser criado.
        '''
        
        with self.assertRaises(IntegrityError):
            user1 = UserFactory(username='myuser1', email='myuser@email.com')

            user2 = UserFactory(username='myuser2', email='myuser@email.com')


    def test_user_model_slug_field(self):
        ''' 
        Descrição:
            Testa o campo slug do modelo User.

        Pré-condições:
            - O modelo User deve estar definido corretamente.

        Pós-condições:
            - O campo slug deve ser criado automaticamente a partir do username do usuário.
        '''

        username = 'Test User Slug'
        self.user = UserFactory(username=username)
        self.assertEqual(self.user.slug, 'test-user-slug')


    def test_user_model_fields_default_visibility(self):
        '''
        Descrição:
            Testa os campos de visibilidade padrão do modelo User.

        Pré-condições:
            - O modelo User deve estar definido corretamente.

        Pós-condições:
            - Os campos de visibilidade padrão devem ser definidos corretamente.
        '''

        user = UserFactory(username='myuser')
        self.assertEqual(user.config_email_visibility, ('QU', 'Qualquer um'))
        self.assertEqual(user.config_status_visibility, ('QU', 'Qualquer um'))
        self.assertEqual(user.config_photo_visibility, ('QU', 'Qualquer um'))


    def test_user_model_fields_choices(self):
        '''
        Descrição:
            Testa as opções de escolha dos campos de visibilidade do modelo User.

        Pré-condições:
            - O modelo User deve estar definido corretamente.

        Pós-condições:
            - As opções de escolha dos campos de visibilidade devem ser definidas corretamente.
        '''

        user = UserFactory(username='myuser')
        self.assertEqual(user.profile_visibility_types, (
            ('QU', 'Qualquer um'),
            ('AA', 'Apenas amigos'),
            ('NM', 'Ninguém'), 
        ))
    
