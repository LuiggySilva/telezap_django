from django.test import TestCase
from django.urls import reverse
from django.contrib.messages import get_messages
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from apps.user.signals import user_logged_out_callback, user_logged_in_callback
from .factories import (
    UserFactory, 
    TextMessageFactory, 
    ImageMessageFactory, 
    ChatFactory, 
    ChatMessageTextFactory, 
    ChatMessageImageFactory,
    ImageMessage,
    TextMessage,
    ChatMessage,
    Chat
)
from factory.django import ImageField
import json


# Desabilita os signals de login e logout para que os testes não sejam afetados
user_logged_in.disconnect(user_logged_in_callback)
user_logged_out.disconnect(user_logged_out_callback)


class ChatsViewTests(TestCase):
    def setUp(self):
        self.user_data = {
            'user1': {
                'username': 'test_user1',
                'password': 'user1@12345',
            },
            'user2': {
                'username': 'test_user2',
                'password': 'user2@12345',
            },
            'user3': {
                'username': 'test_user3',
                'password': 'user3@12345',
            },
        }
        self.user1 = UserFactory(**self.user_data['user1'], photo=ImageField())
        self.user2 = UserFactory(**self.user_data['user2'], photo=ImageField())
        self.user3 = UserFactory(**self.user_data['user3'], photo=ImageField())

    def tearDown(self):
        self.user1.photo.delete()
        self.user2.photo.delete()
        self.user3.photo.delete()


    def test_chats_view_success(self):
        '''
        Description:
            This test verifies that the chats view is being rendered correctly

        Pre-conditions:
            - User is logged in
            - User has no chats

        Post-conditions:
            - User is redirected to the chats view with status code 200
            - The chats view use the template 'chat/chat_list.html'
            - The chats view contains the message 'Nenhuma conversa'
        '''
        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        response = self.client.get(reverse('chat:chats'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_list.html')
        self.assertContains(response, 'Nenhuma conversa')

        self.client.logout()


    def test_chats_view_not_logged_in(self):
        '''
        Description:
            This test verifies that the chats view is being redirected to the login view when the user is not logged in

        Pre-conditions:
            - User is not logged in
            - User tries to access the chats view
        
        Post-conditions:
            - User is redirected to the login view with status code 302
        '''

        response = self.client.get(reverse('chat:chats'), follow=True)

        self.assertRedirects(response, reverse('login') + '?next=' + reverse('chat:chats'))


    def test_chats_view_with_chat(self):
        '''
        Description:
            This test verifies that the chats view is being rendered correctly when the user has a chat

        Pre-conditions:
            - User is logged in
            - User has a chat

        Post-conditions:
            - User is redirected to the chats view with status code 200
            - The chats view use the template 'chat/chat_list.html'
            - The chats view contains the username of the other user in the chat
            - The chats view does not contain the username of a user that is not in the chat
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        response = self.client.get(reverse('chat:chats'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_list.html')
        self.assertContains(response, self.user2.username)
        self.assertNotContains(response, self.user3.username)

        self.client.logout()


    def test_chats_view_with_chats(self):
        '''
        Description:
            This test verifies that the chats view is being rendered correctly when the user has multiple chats

        Pre-conditions:
            - User is logged in
            - User has multiple chats

        Post-conditions:
            - User is redirected to the chats view with status code 200
            - The chats view use the template 'chat/chat_list.html'
            - The chats view contains the username of the other user in each chat
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat1 = ChatFactory(user1=self.user1, user2=self.user2)
        chat2 = ChatFactory(user1=self.user1, user2=self.user3)
        response = self.client.get(reverse('chat:chats'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_list.html')
        self.assertContains(response, self.user2.username)
        self.assertContains(response, self.user3.username)

        self.client.logout()


    def test_chats_view_with_false_user_view_chat(self):
        '''
        Description:
            This test verifies that the chats view is being rendered correctly when the user has a chat with user_view=False

        Pre-conditions:
            - User is logged in
            - User has a chat with user_view=False

        Post-conditions:
            - User is redirected to the chats view with status code 200
            - The chats view use the template 'chat/chat_list.html'
            - The chats view contains the message 'Nenhuma conversa'
            - The chats view does not contain the username of the other user in the chat
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2, user1_view=False)
        response = self.client.get(reverse('chat:chats'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_list.html')
        self.assertContains(response, 'Nenhuma conversa')
        self.assertNotContains(response, self.user2.username)

        self.client.logout()


    def test_chats_view_with_chat_and_messages(self):
        '''
        Description:
            This test verifies that the chats view is being rendered correctly when the user has a chat with messages

        Pre-conditions:
            - User is logged in
            - User has a chat with messages

        Post-conditions:
            - User is redirected to the chats view with status code 200
            - The chats view use the template 'chat/chat_list.html'
            - The chats view contains the username of the other user in the chat
            - The chats view contains the last message of the chat
            - The chats view contains the number of unread messages
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        message1 = TextMessageFactory(author=self.user2)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=message1)
        message2 = TextMessageFactory(author=self.user2)
        chat_message2 = ChatMessageTextFactory(chat=chat, message=message2)
        response = self.client.get(reverse('chat:chats'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat_list.html')
        self.assertContains(response, self.user2.username)
        self.assertContains(response, chat_message2.message.text)
        self.assertContains(response, '2')

        self.client.logout()



class ChatViewTest(TestCase):
    def setUp(self):
        self.user_data = {
            'user1': {
                'username': 'test_user1',
                'password': 'user1@12345',
            },
            'user2': {
                'username': 'test_user2',
                'password': 'user2@12345',
            },
            'user3': {
                'username': 'test_user3',
                'password': 'user3@12345',
            },
        }
        self.user1 = UserFactory(**self.user_data['user1'], photo=ImageField())
        self.user2 = UserFactory(**self.user_data['user2'], photo=ImageField())
        self.user3 = UserFactory(**self.user_data['user3'], photo=ImageField())

    def tearDown(self):
        self.user1.photo.delete()
        self.user2.photo.delete()
        self.user3.photo.delete()


    def test_chat_view_success(self):
        '''
        Description:
            This test verifies that the chat view is being rendered correctly

        Pre-conditions:
            - User is logged in
            - User has a chat

        Post-conditions:
            - User is redirected to the chat view with status code 200
            - The chat view use the template 'chat/chat.html'
            - The response contains the message 'Nenhuma mensagem'
            - The chat view context contains the chat object
            - The chat view context contains the other user in the chat
            - The chat view context contains the emojis list
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        response = self.client.get(reverse('chat:chat', kwargs={'id': chat.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'chat/chat.html')
        self.assertContains(response, 'Nenhuma mensagem')

        self.assertEqual(response.context['chat'], chat)
        self.assertEqual(response.context['another_user'], self.user2)
        self.assertIn('emojis', response.context.keys())

        self.client.logout()


    def test_chat_view_not_logged_in(self):
        '''
        Description:
            This test verifies that the chat view is being redirected to the login view when the user is not logged in

        Pre-conditions:
            - User is not logged in
            - User tries to access the chat view

        Post-conditions:
            - User is redirected to the login view with status code 302
        '''

        chat = ChatFactory(user1=self.user1, user2=self.user2)
        response = self.client.get(reverse('chat:chat', kwargs={'id': chat.id}), follow=True)

        self.assertRedirects(response, reverse('login') + '?next=' + reverse('chat:chat', kwargs={'id': chat.id}))


    def test_chat_view_not_chat_user(self):
        '''
        Description:
            This test verifies that the chat view is being redirected to the chats view when the user is not in the chat

        Pre-conditions:
            - User is logged in
            - User is not in the chat
            - User tries to access the chat view

        Post-conditions:
            - User is redirected to the chats view with status code 302
            - The chats view contains the message 'Você não tem permissão para acessar este chat.'
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        chat = ChatFactory(user1=self.user2, user2=self.user3)
        response = self.client.get(reverse('chat:chat', kwargs={'id': chat.id}), follow=True)

        self.assertRedirects(response, reverse('chat:chats'))
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Você não tem permissão para acessar este chat.', messages)

        self.client.logout()

    
    def test_chat_view_not_found(self):
        '''
        Description:
            This test verifies that the chat view is being redirected to the chats view when the chat does not exist

        Pre-conditions:
            - User is logged in
            - Chat does not exist
            - User tries to access the chat view

        Post-conditions:
            - Return response with status code 404
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        response = self.client.get(reverse('chat:chat', kwargs={'id': '12345678-1234-1234-1234-123456789012'}), follow=True)

        self.assertEqual(response.status_code, 404)

        self.client.logout()



def create_chat_messages(chat, user, num_messages, message_factory, chat_message_factory, visualized=False):
    '''
    Function to create chat messages for testing

    Args:
        chat: Chat object
        user: User object
        num_messages: number of messages to create
        message_factory: factory to create the message
        chat_message_factory: factory to create the chat message
        visualized: if the message is visualized or not

    Returns:
        chat_messages: list of ChatMessage objects
    '''

    chat_messages = []

    for _ in range(num_messages):
        message = message_factory(author=user)
        chat_message = chat_message_factory(chat=chat, message=message, visualized=visualized)
        chat_messages.append(chat_message)

    return chat_messages

class GetChatMessagesViewTest(TestCase):
    def setUp(self):
        self.user_data = {
            'user1': {
                'username': 'test_user1',
                'password': 'user1@12345',
            },
            'user2': {
                'username': 'test_user2',
                'password': 'user2@12345',
            },
            'user3': {
                'username': 'test_user3',
                'password': 'user3@12345',
            },
        }
        self.user1 = UserFactory(**self.user_data['user1'], photo=ImageField())
        self.user2 = UserFactory(**self.user_data['user2'], photo=ImageField())
        self.user3 = UserFactory(**self.user_data['user3'], photo=ImageField())

    def tearDown(self):
        self.user1.photo.delete()
        self.user2.photo.delete()
        self.user3.photo.delete()

        # delete the image file after the test
        image_messages = ImageMessage.objects.filter(author=self.user2)
        if image_messages.exists():
            for image_message in image_messages:
                image_message.image.delete()


    def test_get_chat_messages_view_success(self):
        '''
        Description:
            This test verifies that the get_chat_messages view works correctly

        Pre-conditions:
            - User is logged in
            - User has a chat with messages

        Post-conditions:
            - Return response with status code 200
            - Return response with empty message_list and has_next=False
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        response = self.client.get(reverse('chat:get_chat_messages', kwargs={'id': chat.id}))

        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(data, {"message_list":None, "has_next":False})

        self.client.logout()


    def test_get_chat_messages_view_not_logged_in(self):
        '''
        Description:
            This test verifies that the get_chat_messages view is being redirected to the login view when the user is not logged in

        Pre-conditions:
            - User is not logged in
            - User tries to access the get_chat_messages view

        Post-conditions:
            - User is redirected to the login view with status code 302
        '''

        chat = ChatFactory(user1=self.user1, user2=self.user2)
        response = self.client.get(reverse('chat:get_chat_messages', kwargs={'id': chat.id}), follow=True)

        self.assertRedirects(response, reverse('login') + '?next=' + reverse('chat:get_chat_messages', kwargs={'id': chat.id}))

    
    def test_get_chat_messages_view_not_chat_user(self):
        '''
        Description:
            This test verifies that the get_chat_messages view is being redirected to the chats view when the user is not in the chat

        Pre-conditions:
            - User is logged in
            - User is not in the chat
            - User tries to access the get_chat_messages view

        Post-conditions:
            - User is redirected to the chats view with status code 302
            - The chats view contains the message 'Você não tem permissão para receber as mensagens desse chat.'
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        chat = ChatFactory(user1=self.user2, user2=self.user3)
        response = self.client.get(reverse('chat:get_chat_messages', kwargs={'id': chat.id}), follow=True)

        self.assertRedirects(response, reverse('chat:chats'))
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Você não tem permissão para receber as mensagens desse chat.', messages)

        self.client.logout()


    def test_get_chat_messages_view_with_messages(self):
        '''
        Description:
            This test verifies that the get_chat_messages view works correctly when the chat has messages

        Pre-conditions:
            - User is logged in
            - User has a chat with messages

        Post-conditions:
            - Return response with status code 200
            - Return response with message_list containing the messages
            - Return response with has_next=False
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        message1 = TextMessageFactory(author=self.user2)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=message1)
        message2 = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=message2)
        response = self.client.get(reverse('chat:get_chat_messages', kwargs={'id': chat.id}))

        data = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data['message_list']), 2)
        self.assertIn(chat_message2.message.image.url, data['message_list'][0]['template'])
        self.assertIn(chat_message1.message.text, data['message_list'][1]['template'])
        self.assertEqual(data['has_next'], False)

        self.client.logout()


    def test_get_chat_messages_view_with_messages_and_pagination(self):
        '''
        Description:
            This test verifies that the get_chat_messages view works correctly when the chat has messages and pagination

        Pre-conditions:
            - User is logged in
            - User has a chat with more messages than the pagination limit

        Post-conditions:
            - Return response with status code 200
            - Return response with message_list containing the messages
            - Return response with has_next=True
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        total_messages = settings.MESSAGES_PAGINATION * 2
        chat_messages = create_chat_messages(
            chat, 
            self.user2, 
            total_messages, 
            TextMessageFactory, 
            ChatMessageTextFactory,
            visualized=True
        )
        # Reverse the list to get the most recent messages first
        chat_messages.reverse()

        # First page
        response = self.client.get(reverse('chat:get_chat_messages', kwargs={'id': chat.id}))
        data = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data['message_list']), settings.MESSAGES_PAGINATION)
        for i in range(settings.MESSAGES_PAGINATION):
            self.assertIn(chat_messages[i].message.text, data['message_list'][i]['template'])
        self.assertEqual(data['has_next'], True)

        # Second page
        response = self.client.get(reverse('chat:get_chat_messages', kwargs={'id': chat.id}) + f'?page={2}')
        data = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data['message_list']), settings.MESSAGES_PAGINATION)
        for i in range(settings.MESSAGES_PAGINATION):
            self.assertIn(chat_messages[i + settings.MESSAGES_PAGINATION].message.text, data['message_list'][i]['template'])
        self.assertEqual(data['has_next'], False)

        self.client.logout()

    
    def test_get_chat_messages_view_with_messages_and_pagination_and_not_visualized_messages(self):
        '''
        Description:
            This test verifies that the get_chat_messages view works correctly when the chat has messages and pagination and not visualized messages

        Pre-conditions:
            - User is logged in
            - User has a chat with more messages than the pagination limit
            - User has messages that are not visualized

        Post-conditions:
            - Return response with status code 200
            - Return response with message_list containing all messages above the pagination limit
            - Return response with has_next=False
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        total_messages = settings.MESSAGES_PAGINATION + 5
        chat_messages = create_chat_messages(
            chat, 
            self.user2, 
            total_messages, 
            TextMessageFactory, 
            ChatMessageTextFactory
        )
        # Reverse the list to get the most recent messages first
        chat_messages.reverse()

        response = self.client.get(reverse('chat:get_chat_messages', kwargs={'id': chat.id}))
        data = json.loads(response.content)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(data['message_list']), total_messages)
        for i in range(total_messages):
            self.assertIn(chat_messages[i].message.text, data['message_list'][i]['template'])
        self.assertEqual(data['has_next'], False)

        self.client.logout()



class NewChatMessageViewTest(TestCase):
    def setUp(self):
        self.user_data = {
            'user1': {
                'username': 'test_user1',
                'password': 'user1@12345',
            },
            'user2': {
                'username': 'test_user2',
                'password': 'user2@12345',
            },
            'user3': {
                'username': 'test_user3',
                'password': 'user3@12345',
            },
        }
        self.user1 = UserFactory(**self.user_data['user1'], photo=ImageField())
        self.user2 = UserFactory(**self.user_data['user2'], photo=ImageField())
        self.user3 = UserFactory(**self.user_data['user3'], photo=ImageField())

    def tearDown(self):
        self.user1.photo.delete()
        self.user2.photo.delete()
        self.user3.photo.delete()

        # delete the image file after the test
        image_messages = ImageMessage.objects.all()
        if image_messages.exists():
            for image_message in image_messages:
                image_message.image.delete()


    def test_new_chat_message_view_success(self):
        '''
        Description:
            This test verifies that the new_chat_message view works correctly

        Pre-conditions:
            - User is logged in
            - User has a chat

        Post-conditions:
            - Return response with status code 204
            - The chat has a new message
            - The new message is created correctly in the database
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        message_text = 'Testing message'
        response = self.client.post(
            reverse('chat:new_chat_message', kwargs={'id': chat.id}), 
            data={'message_type': 'T', 'text': message_text}, 
            follow=True
        )

        self.assertEquals(response.status_code, 204)

        self.assertEquals(ChatMessage.objects.filter(chat=chat).count(), 1)
        chat_message = ChatMessage.objects.get(chat=chat)
        self.assertEquals(chat_message.get_message().text, message_text)

        self.client.logout()


    def test_new_chat_message_view_not_logged_in(self):
        '''
        Description:
            This test verifies that the new_chat_message view is being redirected to the login view when the user is not logged in

        Pre-conditions:
            - User is not logged in
            - User tries to access the new_chat_message view

        Post-conditions:
            - User is redirected to the login view with status code 302
        '''

        chat = ChatFactory(user1=self.user1, user2=self.user2)
        message_text = 'Testing message'
        response = self.client.post(
            reverse('chat:new_chat_message', kwargs={'id': chat.id}), 
            data={'message_type': 'T', 'text': message_text}, 
            follow=True
        )

        self.assertRedirects(response, reverse('login') + '?next=' + reverse('chat:new_chat_message', kwargs={'id': chat.id}))


    def test_new_chat_message_view_not_chat_user(self):
        '''
        Description:
            This test verifies that the new_chat_message view is being redirected to the chats view when the user is not in the chat

        Pre-conditions:
            - User is logged in
            - User is not in the chat
            - User tries to access the new_chat_message view

        Post-conditions:
            - User is redirected to the chats view with status code 302
            - The chats view contains the message 'Você não tem permissão para enviar mensagens neste chat.'
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        chat = ChatFactory(user1=self.user2, user2=self.user3)
        message_text = 'Testing message'
        response = self.client.post(
            reverse('chat:new_chat_message', kwargs={'id': chat.id}), 
            data={'message_type': 'T', 'text': message_text}, 
            follow=True
        )

        self.assertRedirects(response, reverse('chat:chats'))
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Você não tem permissão para enviar mensagens neste chat.', messages)

        self.client.logout()


    def test_new_chat_message_view_with_image_message(self):
        '''
        Description:
            This test verifies that the new_chat_message view works correctly when the message is an image

        Pre-conditions:
            - User is logged in
            - User has a chat

        Post-conditions:
            - Return response with status code 204
            - The chat has a new message
            - The new message is created correctly in the database
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        image = SimpleUploadedFile("test_image.jpg", b"image_content")
        response = self.client.post(
            reverse('chat:new_chat_message', kwargs={'id': chat.id}), 
            data={'message_type': 'I', 'image': image}, 
            follow=True
        )

        self.assertEquals(response.status_code, 204)

        self.assertEquals(ChatMessage.objects.filter(chat=chat).count(), 1)
        chat_message = ChatMessage.objects.get(chat=chat)
        self.assertIn(image.name, chat_message.get_message().image.name)

        self.client.logout()


    def test_new_chat_message_view_with_invalid_message_type(self):
        '''
        Description:
            This test verifies that the new_chat_message view works correctly when the message type is invalid

        Pre-conditions:
            - User is logged in
            - User has a chat
            - User tries to send a message with an invalid message type

        Post-conditions:
            - Return response with status code 400
            - The chat has no new messages
            - The chat view contains the message 'Tipo de mensagem inválido.'
        '''

        self.client.login(username=self.user1.email, password=self.user_data['user1']['password'])
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        message_text = 'Testing message'
        response = self.client.post(
            reverse('chat:new_chat_message', kwargs={'id': chat.id}), 
            data={'message_type': 'X', 'text': message_text}, 
            follow=True
        )

        self.assertRedirects(response, reverse('chat:chat', kwargs={'id': chat.id}))
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn('Tipo de mensagem inválido.', messages)
        self.assertEquals(ChatMessage.objects.filter(chat=chat).count(), 0)

        self.client.logout()
