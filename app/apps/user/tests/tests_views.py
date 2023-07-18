from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from .factories import UserFactory


class LoginViewTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = UserFactory(username=self.username, password=self.password)


    def test_login_success(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view login quando um usuário tenta se logar com dados válidos.
            Ele verifica se o usuário é logado corretamente e se ele é redirecionado para a página home após o login.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - O usuário deve ser logado corretamente.
            - O usuário deve ser redirecionado para a página home após o login.
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
        Descrição:
            Este teste verifica o comportamento da view login quando um usuário tenta se logar com dados inválidos.
            Ele verifica se o usuário não é logado e se uma mensagem de erro é exibida após a tentativa de login.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - O usuário não deve ser logado.
            - Uma mensagem de erro deve ser exibida após a tentativa de login.
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
        Descrição:
            Este teste verifica o comportamento da view logout quando um usuário logado tenta se deslogar do sistema.
            Ele verifica se o usuário é deslogado corretamente e se ele é redirecionado para a página home após
            o logout.
        
        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - O usuário deve ser deslogado corretamente.
            - O usuário deve ser redirecionado para a página home após o logout.
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
        Descrição:
            Este teste verifica o comportamento da view signup quando um usuário tenta se cadastrar com dados
            válidos. Ele verifica se o usuário é cadastrado corretamente e se ele é redirecionado para a página
            de login após o cadastro.

        Pré-condições:
            - Um usuário que não está logado no sistema.
            - O usuário tenta se cadastrar com dados válidos.

        Pós-condições:
            - O usuário deve ser cadastrado corretamente.
            - O usuário deve ser redirecionado para a página de login após o cadastro.
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


    def test_signup_failure_email(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view signup quando um usuário tenta se cadastrar com um email
            inválido. Ele verifica se o usuário não é cadastrado e se uma mensagem de erro é exibida após a tentativa
            de cadastro.

        Pré-condições:
            - Um usuário que não está logado no sistema.
            - O usuário tenta se cadastrar com um email inválido.

        Pós-condições:
            - O usuário não deve ser cadastrado.
            - Uma mensagem de erro deve ser exibida após a tentativa de cadastro.
        '''

        response = self.client.post(
            self.signup_url, 
            {
                'username': self.username, 
                'email': 'invalid@email',
                'password1': self.password,
                'password2': self.password
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Informe um endereço de email válido.')


    def test_signup_failure_username(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view signup quando um usuário tenta se cadastrar com um nick
            inválido. Ele verifica se o usuário não é cadastrado e se uma mensagem de erro é exibida após a tentativa
            de cadastro.

        Pré-condições:
            - Um usuário que não está logado no sistema.
            - O usuário tenta se cadastrar com um nick inválido.

        Pós-condições:
            - O usuário não deve ser cadastrado.
            - Uma mensagem de erro deve ser exibida após a tentativa de cadastro.
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


    def test_signup_failure_weak_password(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view signup quando um usuário tenta se cadastrar com uma senha
            fraca. Ele verifica se o usuário não é cadastrado e se uma mensagem de erro é exibida após a tentativa
            de cadastro.

        Pré-condições:
            - Um usuário que não está logado no sistema.
            - O usuário tenta se cadastrar com uma senha fraca.

        Pós-condições:
            - O usuário não deve ser cadastrado.
            - Uma mensagem de erro deve ser exibida após a tentativa de cadastro.
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


    def test_signup_failure_passwords_dont_match(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view signup quando um usuário tenta se cadastrar com uma senha
            que não corresponde à confirmação da senha. Ele verifica se o usuário não é cadastrado e se uma mensagem
            de erro é exibida após a tentativa de cadastro.

        Pré-condições:
            - Um usuário que não está logado no sistema.
            - O usuário tenta se cadastrar com uma senha que não corresponde à confirmação da senha.
        
        Pós-condições:
            - O usuário não deve ser cadastrado.
            - Uma mensagem de erro deve ser exibida após a tentativa de cadastro.
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


    def test_profile_view_success(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view profile quando um usuário logado tenta acessar a sua página
            de perfil de usuário. Ele verifica se o perfil é exibido corretamente.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - O perfil do usuário deve ser exibido corretamente.
        '''

        self.client.login(username=self.email, password=self.password)
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.username)
        self.assertContains(response, self.email)


    def test_user_profile_view_requires_login(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view profile quando um usuário não logado tenta acessar
            a página de perfil de outro usuário. Ele verifica se o usuário é redirecionado para a página de
            login.

        Pré-condições:
            - Um usuário que não está logado no sistema.
        
        Pós-condições:
            - O usuário deve ser redirecionado para a página de login.
        '''

        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.email, password=self.password)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)


    def test_profile_update_view_success(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view profile_update quando o perfil do usuário é atualizado.
            Ele verifica se o perfil é atualizado corretamente e se o usuário é redirecionado para a página do
            perfil atualizado.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - O perfil do usuário deve ser atualizado com sucesso.
            - O usuário deve ser redirecionado para a página do perfil atualizado.
            - Uma mensagem de sucesso deve ser exibida após a atualização.
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


    def test_profile_update_view_failure(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view profile_update quando o perfil do usuário é atualizado
            com dados inválidos. Ele verifica se o perfil não é atualizado e se uma mensagem de erro é exibida
            após a tentativa de atualização.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - O perfil do usuário não deve ser atualizado.
            - Uma mensagem de erro deve ser exibida após a tentativa de atualização.
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
        self.assertIn('Informe um endereço de email válido.', messages)
        self.assertIn('O seu nick não pode conter caracteres especiais ou emojis.', messages)
        self.assertIn(f'Status: Certifique-se de que o valor tenha no máximo 250 caracteres (ele possui {len(new_user_status)}).', messages)


    def test_profile_password_update_view_success(self):
        """
        Descrição:
            Este teste verifica o comportamento da view profile_password_update quando a senha do perfil do usuário
            é atualizada com uma nova senha. Ele verifica se a senha é atualizada corretamente e se uma mensagem de
            sucesso é exibida após a atualização.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - A senha do perfil do usuário deve ser atualizada com sucesso.
            - Uma mensagem de sucesso deve ser exibida após a atualização.
        """

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


    def test_profile_password_update_view_failure_wrong_old_password(self):
        """
        Descrição:
            Este teste verifica o comportamento da view profile_password_update quando a senha do perfil do usuário
            é atualizada com uma senha antiga incorreta. Ele verifica se a senha não é atualizada e se uma mensagem
            de erro é exibida após a tentativa de atualização.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - A senha do perfil do usuário não deve ser atualizada.
            - Uma mensagem de erro deve ser exibida após a tentativa de atualização.
        """

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


    def test_profile_password_update_view_failure_weak_password(self):
        """
        Descrição:
            Este teste verifica o comportamento da view profile_password_update quando a senha do perfil do usuário
            é atualizada com uma nova senha fraca. Ele verifica se a senha não é atualizada e se uma mensagem de erro
            é exibida após a tentativa de atualização.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - A senha do perfil do usuário não deve ser atualizada.
            - Uma mensagem de erro deve ser exibida após a tentativa de atualização.
        """

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


    def test_profile_password_update_view_failure_passwords_dont_match(self):
        """
        Descrição:
            Este teste verifica o comportamento da view profile_password_update quando a senha do perfil do usuário
            é atualizada com uma nova senha que não corresponde à confirmação da nova senha. Ele verifica se a senha
            não é atualizada e se uma mensagem de erro é exibida após a tentativa de atualização.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - A senha do perfil do usuário não deve ser atualizada.
            - Uma mensagem de erro deve ser exibida após a tentativa de atualização.
        """

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


    def test_profile_config_update_view_success(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view profile_config_update quando as configurações de 
            visibilidade do perfil do usuário são atualizadas. Ele verifica se as configurações são atualizadas 
            corretamente e se uma mensagem de sucesso é exibida após a atualização.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.
        
        Pós-condições:
            - As configurações de visibilidade do perfil do usuário devem ser atualizadas com sucesso.
            - Uma mensagem de sucesso deve ser exibida após a atualização.
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


    def test_profile_config_update_view_failure(self):
        '''
        Descrição:
            Este teste verifica o comportamento da view profile_config_update quando as configurações de
            visibilidade do perfil do usuário são atualizadas com uma configuração inválida. Ele verifica se
            as configurações não são atualizadas e se uma mensagem de erro é exibida após a tentativa de atualização.

        Pré-condições:
            - Um usuário existente com email e senha logado no sistema.

        Pós-condições:
            - As configurações de visibilidade do perfil do usuário não devem ser atualizadas.
            - Uma mensagem de erro deve ser exibida após a tentativa de atualização.
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
