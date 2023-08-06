from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from .factories import UserFactory, User


class LoginViewTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = UserFactory(username=self.username, password=self.password)


    def test_login_success(self):
        '''
        Description:
            This test verifies the behavior of the login view when a user tries to log in with valid data.
            It verifies that the user is logged in correctly and that he is redirected to the home page after login.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user must be logged in correctly.
            - The user must be redirected to the home page after login.
        '''

        response = self.client.post(
            self.login_url, 
            {
                'username': self.username, 
                'password': self.password
            },
        )
        self.assertEqual(response.status_code, 200)


    def test_login_failure(self):
        '''
        Description:
            This test verifies the behavior of the login view when a user tries to log in with invalid data.
            It verifies that the user is not logged in and that an error message is displayed after the login attempt.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user must not be logged in.
            - An error message must be displayed after the login attempt.
        '''
        
        response = self.client.post(
            self.login_url, 
            {
                'username': self.username, 
                'password': 'wrongpassword'
            }
        )
        self.assertEqual(response.status_code, 200)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.logout_url = reverse('logout')
        self.redirect_url = reverse('user:landing_page')

    def test_logout_success(self):
        '''
        Description:
            This test verifies the behavior of the logout view when a logged in user tries to log out of the system.
            It verifies that the user is logged out correctly and that he is redirected to the home page after
            logout.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user must be logged out correctly.
            - The user must be redirected to the home page after logout.
        '''

        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.redirect_url)
        

class SignupViewTests(TestCase):
    def setUp(self):
        self.signup_url = reverse('signup')
        self.username = 'testuser'
        self.email = 'testuser@email.com'
        self.password = 'testpassword'

    def test_signup_success(self):
        '''
        Description:
            This test verifies the behavior of the signup view when a user tries to sign up with valid data.
            It verifies that the user is signed up correctly and that he is redirected to the login page after
            signup.

        Pre-conditions:
            - A user who is not logged into the system.
            - The user tries to sign up with valid data.

        Post-conditions:
            - The user must be signed up correctly.
            - The user must be redirected to the login page after signup.
            - The user is saved in the database.
        '''

        response = self.client.post(
            self.signup_url, 
            {
                'username': self.username, 
                'email': self.email,
                'password1': self.password,
                'password2': self.password
            }
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(email=self.email).exists())

    def test_signup_failure_username(self):
        '''
        Description:
            This test verifies the behavior of the signup view when a user tries to sign up with an invalid username.
            It verifies that the user is not signed up and that an error message is displayed after the signup attempt.

        Pre-conditions:
            - A user who is not logged into the system.
            - The user tries to sign up with an invalid username.

        Post-conditions:
            - The user must not be signed up.
            - An error message must be displayed after the signup attempt.
        '''
        
        response = self.client.post(
            self.signup_url, 
            {
                'username': 'invalid@123🤡', 
                'email': self.email,
                'password1': self.password,
                'password2': self.password
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'O seu nick não pode conter caracteres especiais ou emojis.')
        self.assertFalse(User.objects.filter(email=self.email).exists())


    def test_signup_failure_weak_password(self):
        '''
        Description:
            This test verifies the behavior of the signup view when a user tries to sign up with a weak password.
            It verifies that the user is not signed up and that an error message is displayed after the signup attempt.

        Pre-conditions:
            - A user who is not logged into the system.
            - The user tries to sign up with a weak password.

        Post-conditions:
            - The user must not be signed up.
            - An error message must be displayed after the signup attempt.
        '''

        response = self.client.post(
            self.signup_url, 
            {
                'username': self.username, 
                'email': self.email,
                'password1': '123',
                'password2': '123'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Esta senha é muito comum.')
        self.assertContains(response, 'Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres.')
        self.assertContains(response, 'Esta senha é inteiramente numérica.')
        self.assertFalse(User.objects.filter(email=self.email).exists())


    def test_signup_failure_passwords_dont_match(self):
        '''
        Description:
            This test verifies the behavior of the signup view when a user tries to sign up with a password that
            does not match the password confirmation. It verifies that the user is not signed up and that an error
            message is displayed after the signup attempt.

        Pre-conditions:
            - A user who is not logged into the system.
            - The user tries to sign up with a password that does not match the password confirmation.

        Post-conditions:
            - The user must not be signed up.
            - An error message must be displayed after the signup attempt.
        '''

        response = self.client.post(
            self.signup_url, 
            {
                'username': self.username, 
                'email': self.email,
                'password1': self.password,
                'password2': 'wrongpassword'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Os dois campos de senha não correspondem.')
        self.assertFalse(User.objects.filter(email=self.email).exists())


class ProfileViewTests(TestCase):
    def setUp(self):
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = UserFactory(username=self.username, password=self.password)
        self.email = self.user.email
        self.profile_url = reverse('user:profile', kwargs={'slug': self.username})
        self.profile_update_url = reverse('user:profile_update', kwargs={'slug': self.username})
        self.profile_password_update_url = reverse('user:profile_password_update', kwargs={'slug': self.username})
        self.profile_config_update_url = reverse('user:profile_config_update', kwargs={'slug': self.username})


    def test_profile_success(self):
        '''
        Description:
            This test verifies the behavior of the profile view when a logged in user tries to access his user profile
            page. It verifies that the profile is displayed correctly.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile must be displayed correctly.
        '''

        self.client.login(username=self.email, password=self.password)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username)
        self.assertContains(response, self.email)


    def test_user_profile_requires_login(self):
        '''
        Description:
            This test verifies the behavior of the profile view when a logged in user tries to access another user's
            profile page. It verifies that the user is redirected to the login page.

        Pre-conditions:
            - A user who is not logged into the system.

        Post-conditions:
            - The user must be redirected to the login page.
        '''

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.email, password=self.password)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)


    def test_profile_update_success(self):
        '''
        Description:
            This test verifies the behavior of the profile_update view when the user's profile is updated.
            It verifies that the profile is updated correctly and that the user is redirected to the updated
            profile page.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile must be updated correctly.
        '''

        self.client.login(username=self.email, password=self.password)
        new_user_name = 'newname'
        new_user_status = 'newstatus'
        new_user_profile_url = reverse('user:profile', kwargs={'slug':  new_user_name})

        response = self.client.post(
            self.profile_update_url, 
            {
                'photo': 'user_profiles_photos/default.jpg', 
                'username': new_user_name,
                'status': new_user_status,
                'email': self.email
            },
            follow=True  # Segue o redirecionamento
        )

        self.assertContains(response, new_user_name)
        self.assertContains(response, new_user_status)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Perfil atualizado com sucesso!', messages)


    def test_profile_update_failure(self):
        '''
        Description:
            This test verifies the behavior of the profile_update view when the user's profile is updated with
            invalid data. It verifies that the profile is not updated and that an error message is displayed after
            the update attempt.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile must not be updated.
            - An error message must be displayed after the update attempt.
        '''

        self.client.login(username=self.email, password=self.password)
        new_user_name = 'InvalidName@123🤡'
        new_user_status = 'tooloongstatus' * 100
        new_user_email = 'wrong@mail'

        response = self.client.post(
            self.profile_update_url, 
            {
                'photo': 'user_profiles_photos/default.jpg', 
                'username': new_user_name,
                'status': new_user_status,
                'email': new_user_email
            },
            follow=True  # Segue o redirecionamento
        )
        self.assertNotContains(response, new_user_name)
        self.assertNotContains(response, new_user_status)
        self.assertNotContains(response, new_user_email)

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Erro na alteração do perfil!', messages)
        self.assertIn('Insira um endereço de email válido.', messages)
        self.assertIn('O seu nick não pode conter caracteres especiais ou emojis.', messages)
        self.assertIn(f'Status: Certifique-se de que o valor tenha no máximo 250 caracteres (ele possui {len(new_user_status)}).', messages)


    def test_profile_password_update_success(self):
        '''
        Description:
            This test verifies the behavior of the profile_password_update view when the user's profile password
            is updated with a new password. It verifies that the password is updated correctly and that a success
            message is displayed after the update.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile password must be updated correctly.
            - A success message must be displayed after the update.
        '''

        self.client.login(username=self.email, password=self.password)
        new_password = 'NewSecuryPassword@123'
        response = self.client.post(
            self.profile_password_update_url, 
            {
                'old_password': self.password, 
                'new_password1': new_password,
                'new_password2': new_password,
            },
            follow=True  # Segue o redirecionamento
        )
        self.assertEqual(response.status_code, 200)
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Senha atualizada com sucesso!', messages)


    def test_profile_password_update_failure_wrong_old_password(self):
        '''
        Description:
            This test verifies the behavior of the profile_password_update view when the user's profile password
            is updated with a wrong old password. It verifies that the password is not updated and that an error
            message is displayed after the update attempt.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile password must not be updated.
            - An error message must be displayed after the update attempt.
        '''

        self.client.login(username=self.email, password=self.password)
        new_password = 'NewSecuryPassword@123'
        response = self.client.post(
            self.profile_password_update_url, 
            {
                'old_password': 'wrongpassword', 
                'new_password1': new_password,
                'new_password2': new_password,
            },
            follow=True  # Segue o redirecionamento
        )
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Erro na alteração da senha!', messages)
        self.assertIn('A senha antiga foi digitada incorretamente. Por favor, informe-a novamente.', messages)


    def test_profile_password_update_failure_weak_password(self):
        '''
        Description:
            This test verifies the behavior of the profile_password_update view when the user's profile password
            is updated with a weak new password. It verifies that the password is not updated and that an error
            message is displayed after the update attempt.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile password must not be updated.
            - An error message must be displayed after the update attempt.
        '''

        self.client.login(username=self.email, password=self.password)
        new_password = '123'
        response = self.client.post(
            self.profile_password_update_url, 
            {
                'old_password': self.password, 
                'new_password1': new_password,
                'new_password2': new_password,
            },
            follow=True  # Segue o redirecionamento
        )
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Erro na alteração da senha!', messages)
        self.assertIn('Esta senha é muito comum.', messages)
        self.assertIn('Esta senha é muito curta. Ela precisa conter pelo menos 8 caracteres.', messages)
        self.assertIn('Esta senha é inteiramente numérica.', messages)


    def test_profile_password_update_failure_passwords_dont_match(self):
        '''
        Description:
            This test verifies the behavior of the profile_password_update view when the user's profile password
            is updated with a new password that does not match the password confirmation. It verifies that the
            password is not updated and that an error message is displayed after the update attempt.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile password must not be updated.
            - An error message must be displayed after the update attempt.
        '''

        self.client.login(username=self.email, password=self.password)
        new_password = 'NewSecuryPassword@123'
        response = self.client.post(
            self.profile_password_update_url,
            {
                'old_password': self.password,
                'new_password1': new_password,
                'new_password2': 'wrongpassword',
            },
            follow=True  # Segue o redirecionamento
        )

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Erro na alteração da senha!', messages)
        self.assertIn('Os dois campos de senha não correspondem.', messages)


    def test_profile_config_update_success(self):
        '''
        Description:
            This test verifies the behavior of the profile_config_update view when the user's profile visibility
            settings are updated. It verifies that the settings are updated correctly and that a success message
            is displayed after the update.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile visibility settings must be updated correctly.
            - A success message must be displayed after the update.
        '''

        self.client.login(username=self.email, password=self.password)
        new_photo_config = 'QU'
        new_email_config = 'AA'
        new_status_config = 'AA'
        new_online_config = 'NM'

        response = self.client.post(
            self.profile_config_update_url, 
            {
                'config_email_visibility': new_email_config,
                'config_photo_visibility': new_photo_config,
                'config_status_visibility': new_status_config,
                'config_online_visibility': new_online_config
            },
            follow=True  # Segue o redirecionamento
        )

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Configurações atualizadas com sucesso!', messages)


    def test_profile_config_update_failure(self):
        '''
        Description:
            This test verifies the behavior of the profile_config_update view when the user's profile visibility
            settings are updated with an invalid configuration. It verifies that the settings are not updated and
            that an error message is displayed after the update attempt.

        Pre-conditions:
            - An existing user with email and password logged into the system.

        Post-conditions:
            - The user profile visibility settings must not be updated.
            - An error message must be displayed after the update attempt.
        '''

        self.client.login(username=self.email, password=self.password)
        new_wrong_email_config = 'wrongconfig'

        response = self.client.post(
            self.profile_config_update_url, 
            {
                'config_email_visibility': new_wrong_email_config,
                'config_photo_visibility': 'QU',
                'config_status_visibility': 'AA',
                'config_online_visibility': 'NM'
            },
            follow=True  # Segue o redirecionamento
        )

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Erro na alteração das configurações!', messages)
        self.assertIn(f'Faça uma escolha válida. {new_wrong_email_config} não é uma das escolhas disponíveis.', messages)
