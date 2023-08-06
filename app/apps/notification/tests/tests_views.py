from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from .factories import UserFactory, FriendshipRequestFactory, GroupRequestFactory, FriendshipRequest, GroupRequest

class NotificationsViewTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.notifications_url = reverse('notification:notifications')
        self.user1_data = {
            'username': 'user1',
            'password': 'User1@123'
        }
        self.user2_data = {
            'username': 'user2',
            'password': 'User2@123'
        }
        self.user1 = UserFactory(**self.user1_data)
        self.user2 = UserFactory(**self.user2_data)
    

    def test_notifications_view_with_get_method(self):
        '''
        Desciption:
            This test verifies the notifications view response with the GET method.
            
        Preconditions:
            - The user must be logged in the system.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The view must contain the text "Enviar solicitação de amizade".
            - The view must contain the text "Solicitações de amizade".
            - The view must contain the text "Solicitações de grupo".
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.get(self.notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        self.assertContains(response, 'Enviar solicitação de amizade')
        self.assertContains(response, 'Solicitações de amizade')
        self.assertContains(response, 'Solicitações de grupo')


    def test_notifications_view_with_post_method(self):
        '''
        Desciption:
            This test verifies the notifications view response with the POST method.

        Preconditions:
            - The user must be logged in the system.
            - The user must send a valid email in the notifications view.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The view must contain the name and email of the user who received the friend request.
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(
            self.notifications_url, 
            {
                'email': self.user2.email
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        self.assertContains(response, self.user2)
        self.assertContains(response, self.user2.email)


    def test_notifications_view_with_post_method_with_not_found_user(self):
        '''
        Desciption:
            This test verifies the notifications view response with the POST method and an invalid user email.

        Preconditions:
            - The user must be logged in the system.
            - The user must send an invalid email in the notifications view.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The view must contain the text "Nenhum usuário com esse email foi encontrado.".
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(
            self.notifications_url, 
            {
                'email': 'randomemail@email.com'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Nenhum usuário com esse email foi encontrado.', messages)

    
    def test_notifications_view_with_post_method_with_self_email(self):
        '''
        Desciption:
            This test verifies the notifications view response with the POST method and the user's own email.

        Preconditions:
            - The user must be logged in the system.
            - The user must send his own email in the notifications view.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The view must contain the text "Você não pode se adicionar como amigo.".
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        self.user1.friends.add(self.user2)
        response = self.client.post(
            self.notifications_url, 
            {
                'email': self.user1.email
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Você não pode se adicionar como amigo.', messages)


class NotificationReplyViewTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.notifications_url = reverse('notification:notifications')
        self.notifications_reply_url = reverse('notification:reply_notification_request')
        self.user1_data = {
            'username': 'user1',
            'password': 'User1@123'
        }
        self.user2_data = {
            'username': 'user2',
            'password': 'User2@123'
        }
        self.user3_data = {
            'username': 'user3',
            'password': 'User3@123'
        }
        self.user1 = UserFactory(**self.user1_data)
        self.user2 = UserFactory(**self.user2_data)
        self.user3 = UserFactory(**self.user3_data)


    def test_reply_notification_view_accept(self):
        '''
        Desciption:
            This test verifies the reply notification view response with the POST method and accept a friend request.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and must contain a pending friend request.
            - The user must send accept this friend request.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The view must not contain the friend request that was accepted.
            - The friend request must have the status "A" of accepted.
            - The friend request must have the receiver view as False.
            - The user must receive a success message.
            - The user must have the other user as a friend.
        '''
  
        notification = FriendshipRequestFactory(author=self.user2, receiver=self.user1)
        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(self.notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        self.assertContains(response, self.user2)
        self.assertContains(response, self.user2.email)

        response = self.client.post(
            self.notifications_reply_url, 
            {
                'notification_id': notification.pk,
                'notification_type': notification.notification_type,
                'reply': True
            },
            follow=True  # Segue o redirecionamento
        )

        notification.refresh_from_db()
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f'{notification.author} agora é seu amigo(a)!', messages)
        self.assertEqual(notification.status, 'A')
        self.assertFalse(notification.receiver_view)

        response = self.client.get(self.notifications_url)
        self.assertNotContains(response, self.user2)
        self.assertNotContains(response, self.user2.email)

        self.assertEqual(notification.author.friends.first(), self.user1)
        self.assertEqual(notification.receiver.friends.first(), self.user2)


    def test_reply_notification_view_reject(self):
        '''
        Desciption:
            This test verifies the reply notification view response with the POST method and reject a friend request.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and must contain a pending friend request.
            - The user must send reject this friend request.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The view must not contain the friend request that was rejected.
            - The friend request must have the status "R" of rejected.
        '''

        notification = FriendshipRequestFactory(author=self.user2, receiver=self.user1)
        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(self.notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        self.assertContains(response, self.user2)
        self.assertContains(response, self.user2.email)

        response = self.client.post(
            self.notifications_reply_url, 
            {
                'notification_id': notification.pk,
                'notification_type': notification.notification_type,
                'reply': False
            },
            follow=True  # Segue o redirecionamento
        )

        notification.refresh_from_db()

        response = self.client.get(self.notifications_url)
        self.assertNotContains(response, self.user2)
        self.assertNotContains(response, self.user2.email)


    def test_reply_notification_view_inexistent(self):
        '''
        Desciption:
            This test verifies the reply notification view response with the POST method and an inexistent notification id.

        Preconditions:
            - The user must be logged in the system.
            - The user must send an inexistent notification id.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The user must receive an error message.
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(self.notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        response = self.client.post(
            self.notifications_reply_url, 
            {
                'notification_id': 999,
                'notification_type': 'A',
                'reply': True
            },
            follow=True  # Segue o redirecionamento
        )

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Notificação não encontrada.', messages)


    def test_reply_notification_view_unauthorized(self):
        '''
        Desciption:
            This test verifies the reply notification view response with the POST method and try to reply a friend request that is not his.

        Preconditions:
            - The user must be logged in the system.
            - The user must send a notification id that is not his.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The user must receive an error message.
        '''

        notification = FriendshipRequestFactory(author=self.user2, receiver=self.user1)
        self.client.login(username=self.user3.email, password=self.user3_data['password'])
        response = self.client.post(self.notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        response = self.client.post(
            self.notifications_reply_url, 
            {
                'notification_id': notification.pk,
                'notification_type': notification.notification_type,
                'reply': True
            },
            follow=True  # Segue o redirecionamento
        )

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Você não tem permissão para realizar essa ação.', messages)


    #TODO: tests to reply group notifications


class RemoveNotificationsVisibilityTests(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.notifications_url = reverse('notification:notifications')
        self.notifications_remove_url = reverse('notification:remove_notifications')
        self.user1_data = {
            'username': 'user1',
            'password': 'User1@123'
        }
        self.user2_data = {
            'username': 'user2',
            'password': 'User2@123'
        }
        self.user3_data = {
            'username': 'user3',
            'password': 'User3@123'
        }
        self.user1 = UserFactory(**self.user1_data)
        self.user2 = UserFactory(**self.user2_data)
        self.user3 = UserFactory(**self.user3_data)

    
    def test_remove_notifications_visibility_view_friends_reply(self):
        '''
        Desciption:
            This test verifies the remove notifications visibility view response with the POST method and remove the visibility of a friend request.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and must contain a finished friend request.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The finished friendship sent/request must have the author/receiver view as False.
            - The finished friendship sent/request must not be in the notifications view.
        '''

        notification1 = FriendshipRequestFactory(author=self.user2, receiver=self.user1, status='A')
        notification2 = FriendshipRequestFactory(author=self.user1, receiver=self.user3, status='R')

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(self.notifications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')
        self.assertContains(response, self.user2)
        self.assertContains(response, self.user2.email)
        self.assertContains(response, self.user3)
        self.assertContains(response, self.user3.email)

        response = self.client.post(
            self.notifications_remove_url, 
            {
                'notification_type': notification1.notification_type
            },
            follow=True  # Segue o redirecionamento
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        notification1.refresh_from_db()
        notification2.refresh_from_db()

        self.assertFalse(notification1.receiver_view)
        self.assertTrue(notification1.author_view)
        self.assertFalse(notification2.author_view)
        self.assertTrue(notification2.receiver_view)

        self.assertNotContains(response, self.user2)
        self.assertNotContains(response, self.user2.email)
        self.assertNotContains(response, self.user3)
        self.assertNotContains(response, self.user3.email)


    #TODO: def test_remove_notifications_visibility_view_groups_reply


class SendFriendRequestTest(TestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.notifications_url = reverse('notification:notifications')
        self.send_friend_request_url = reverse('notification:send_friend_request')
        self.user1_data = {
            'username': 'user1',
            'password': 'User1@123'
        }
        self.user2_data = {
            'username': 'user2',
            'password': 'User2@123'
        }
        self.user3_data = {
            'username': 'user3',
            'password': 'User3@123'
        }
        self.user1 = UserFactory(**self.user1_data)
        self.user2 = UserFactory(**self.user2_data)
        self.user3 = UserFactory(**self.user3_data)


    def test_send_friend_request_view(self):
        '''
        Desciption:
            This test verifies the send friend request view response with the POST method and send a friendship request.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and send a valid friend request.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The user must be redirected to the notifications view.
            - The user must receive a success message.
            - The friendship request must be in the database.
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(
            self.send_friend_request_url, 
            {
                'email': self.user2.email
            },
            follow=True  # Segue o redirecionamento
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f"Solicitação de amizade enviada para '{self.user2.email}' com sucesso!", messages)
        self.assertTrue(FriendshipRequest.objects.filter(author=self.user1, receiver=self.user2).exists())

    
    def test_send_friend_request_view_with_invalid_email(self):
        '''
        Description:
            This test verifies the send friend request view response with the POST method and send a friendship request with an invalid email.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and send an friendship request with invalid email.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The user must be redirected to the notifications view.
            - The user must receive an error message.
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(
            self.send_friend_request_url, 
            {
                'email': 'notexists@email.com'
            },
            follow=True  # Segue o redirecionamento
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f"Nenhum usuário(a) com esse email foi encontrado.", messages)

    
    def test_send_friend_request_view_with_self_email(self):
        '''
        Description:
            This test verifies the send friend request view response with the POST method and send a friendship request with his own email.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and send an friendship request with his own email.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The user must be redirected to the notifications view.
            - The user must receive an error message.
        '''

        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(
            self.send_friend_request_url, 
            {
                'email': self.user1.email
            },
            follow=True  # Segue o redirecionamento
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f"Você não pode se adicionar como amigo.", messages)


    def test_send_friend_request_view_already_friends(self):
        '''
        Description:
            This test verifies the send friend request view response with the POST method and send a friendship request to a user who is already his friend.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and send an friendship request to a user who is already his friend.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The user must be redirected to the notifications view.
        '''

        self.user1.friends.add(self.user2)
        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(
            self.send_friend_request_url, 
            {
                'email': self.user2.email
            },
            follow=True  # Segue o redirecionamento
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f"Você já é amigo desse usuário(a).", messages)


    def test_send_friend_request_view_already_send(self):
        '''
        Description:
            This test verifies the send friend request view response with the POST method and send a friendship request to a user who already received a friendship request from him.

        Preconditions:
            - The user must be logged in the system.
            - The user must be in the notifications view and send an friendship request to a user who already received a friendship request from him.

        Postconditions:
            - The view must return the template notification/notifications.html.
            - The view must return the status code 200.
            - The user must be redirected to the notifications view.
            - The user must receive an error message.
        '''

        notification = FriendshipRequestFactory(author=self.user1, receiver=self.user2)
        self.client.login(username=self.user1.email, password=self.user1_data['password'])
        response = self.client.post(
            self.send_friend_request_url, 
            {
                'email': self.user2.email
            },
            follow=True  # Segue o redirecionamento
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notification/notifications.html')

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn(f"Você já enviou uma solicitação de amizade para esse usuário(a).", messages)
