from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.db import transaction

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


class TextMessageTest(TestCase):
    def setUp(self):
        self.user1_data = {
            'username': 'user1',
            'password': 'User1@123'
        }
        self.user1 = UserFactory(**self.user1_data)
    

    def test_text_message_model_str_method(self):
        '''
        Description:
            Tests the __str__ method of the TextMessage model.

        Pre-conditions:
            - The TextMessage model must be correctly defined.

        Post-conditions:
            - The __str__ method must return the id, the author and the message type of the message.
        '''
        
        text_message = TextMessageFactory(author=self.user1)
        self.assertEqual(str(text_message), f"{text_message.id} - {self.user1.email} - Texto")



class ImageMessageTest(TestCase):
    def setUp(self):
        self.user1_data = {
            'username': 'user1',
            'password': 'User1@123'
        }
        self.user1 = UserFactory(**self.user1_data)

    def tearDown(self):
        # delete the image file after the test
        ImageMessage.objects.get(author=self.user1).image.delete()

    def test_image_message_model_str_method(self):
        '''
        Description:
            Tests the __str__ method of the ImageMessage model.

        Pre-conditions:
            - The ImageMessage model must be correctly defined.

        Post-conditions:
            - The __str__ method must return the id, the author and the message type of the message.
        '''
        
        image_message = ImageMessageFactory(author=self.user1)
        self.assertEqual(str(image_message), f"{image_message.id} - {self.user1.email} - Imagem")



class ChatTest(TestCase):
    def setUp(self):
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

    def tearDown(self):
        # delete the image file after the test
        image_messages = ImageMessage.objects.filter(author=self.user2)
        if image_messages.exists():
            for image_message in image_messages:
                image_message.image.delete()


    def test_chat_model_str_method(self):
        '''
        Description:
            Tests the __str__ method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The __str__ method must return the id, the user 1 and the user 2 of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertEqual(str(chat), f"{self.user1.email} - {self.user2.email}")


    def test_chat_model_default_values(self):
        '''
        Description:
            Tests the default values of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The default values must be True for the user 1 and the user 2 view.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertTrue(chat.user1_view)
        self.assertTrue(chat.user2_view)


    def test_chat_model_unique_together(self):
        '''
        Description:
            Tests the unique_together of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The unique_together must be the user 1 and the user 2 of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ChatFactory(user1=self.user1, user2=self.user2)


    def test_chat_model_get_another_user_method(self):
        '''
        Description:
            Tests the get_another_user method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_another_user method must return the other user of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertEqual(chat.get_another_user(self.user1), self.user2)
        self.assertEqual(chat.get_another_user(self.user2), self.user1)


    def test_chat_model_get_another_user_method_error(self):
        '''
        Description:
            Tests the get_another_user method of the Chat model when the user passed is not in the chat.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_another_user method must raise a ValidationError.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertRaises(ValidationError, chat.get_another_user, self.user3)


    def test_chat_model_update_messages_visualization_method(self):
        '''
        Description:
            Tests the update_messages_visualization method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The update_messages_visualization method must update the messages of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        text_message = TextMessageFactory(author=self.user1)
        chat_message = ChatMessageTextFactory(chat=chat, message=text_message, visualized=False)
        chat.update_messages_visualization(self.user2)
        chat_message.refresh_from_db()
        self.assertTrue(chat_message.visualized)


    def test_chat_model_update_messages_visualization_method_error(self):
        '''
        Description:
            Tests the update_messages_visualization method of the Chat model when the user passed is not in the chat.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The update_messages_visualization method must raise a ValidationError.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertRaises(ValidationError, chat.update_messages_visualization, self.user3)


    def test_chat_model_get_messages_method(self):
        '''
        Description:
            Tests the get_messages method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_messages method must return the messages of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertIsNone(chat.get_messages())

        text_message = TextMessageFactory(author=self.user1)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=text_message, visualized=False)
        image_message = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=image_message, visualized=False)

        self.assertEqual(chat.get_messages(), [image_message, text_message])


    def test_chat_model_get_last_message_method(self):
        '''
        Description:
            Tests the get_last_message method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_last_message method must return the last message of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertIsNone(chat.get_last_message())

        text_message = TextMessageFactory(author=self.user1)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=text_message, visualized=False)
        image_message = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=image_message, visualized=False)

        self.assertEqual(chat.get_last_message(), image_message)


    def test_chat_model_get_last_message_method_with_date(self):
        '''
        Description:
            Tests the get_last_message method of the Chat model with date=True.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_last_message method must return the last message of the chat and the date of the message.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertIsNone(chat.get_last_message(date=True))

        text_message = TextMessageFactory(author=self.user1)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=text_message, visualized=False)
        image_message = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=image_message, visualized=False)

        self.assertEqual(chat.get_last_message(date=True), (image_message, chat_message2.message.date))


    def test_chat_model_get_amount_of_messages_method(self):
        '''
        Description:
            Tests the get_amount_of_messages method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_amount_of_messages method must return the amount of messages of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertEqual(chat.get_amount_of_messages(), 0)

        text_message = TextMessageFactory(author=self.user1)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=text_message, visualized=False)
        image_message = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=image_message, visualized=False)

        self.assertEqual(chat.get_amount_of_messages(), 2)


    def test_chat_model_get_amount_of_unviewed_messages_method(self):
        '''
        Description:
            Tests the get_amount_of_unviewed_messages method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_amount_of_unviewed_messages method must return the amount of unvisualized messages of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertEqual(chat.get_amount_of_unviewed_messages(self.user1), 0)
        self.assertEqual(chat.get_amount_of_unviewed_messages(self.user2), 0)

        text_message1 = TextMessageFactory(author=self.user1)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=text_message1, visualized=False)
        image_message = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=image_message, visualized=False)
        text_message2 = TextMessageFactory(author=self.user1)
        chat_message3 = ChatMessageTextFactory(chat=chat, message=text_message2, visualized=True)

        self.assertEqual(chat.get_amount_of_unviewed_messages(self.user1), 1)
        self.assertEqual(chat.get_amount_of_unviewed_messages(self.user2), 1)


    def test_chat_model_have_unviewed_nessage(self):
        '''
        Description:
            Tests the have_unviewed_message method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The have_unviewed_message method must return True if the user has unvisualized messages.
            - The have_unviewed_message method must return False if the user has not unvisualized messages.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertFalse(chat.have_unviewed_message(self.user1))
        self.assertFalse(chat.have_unviewed_message(self.user2))

        text_message1 = TextMessageFactory(author=self.user1)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=text_message1, visualized=False)
        image_message = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=image_message, visualized=True)

        self.assertFalse(chat.have_unviewed_message(self.user1))
        self.assertTrue(chat.have_unviewed_message(self.user2))
    

    def test_chat_model_get_first_unviewed_message(self):
        '''
        Description:
            Tests the get_first_unviewed_message method of the Chat model.

        Pre-conditions:
            - The Chat model must be correctly defined.

        Post-conditions:
            - The get_first_unviewed_message method must return the first unviewed message of the chat.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        self.assertIsNone(chat.get_first_unviewed_message(self.user1))
        self.assertIsNone(chat.get_first_unviewed_message(self.user2))

        text_message1 = TextMessageFactory(author=self.user1)
        chat_message1 = ChatMessageTextFactory(chat=chat, message=text_message1, visualized=False)
        image_message = ImageMessageFactory(author=self.user2)
        chat_message2 = ChatMessageImageFactory(chat=chat, message=image_message, visualized=True)
        text_message2 = TextMessageFactory(author=self.user1)
        chat_message3 = ChatMessageTextFactory(chat=chat, message=text_message2, visualized=False)

        self.assertIsNone(chat.get_first_unviewed_message(self.user1))
        self.assertEqual(chat.get_first_unviewed_message(self.user2), text_message1.id)



class ChatMessageTest(TestCase):
    def setUp(self):
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


    def test_chatmessage_model_str_method(self):
        '''
        Description:
            Tests the __str__ method of the ChatMessage model.

        Pre-conditions:
            - The ChatMessage model must be correctly defined.

        Post-conditions:
            - The __str__ method must return the id, the chat and the message of the chat message.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        text_message = TextMessageFactory(author=self.user1)
        chat_message = ChatMessageTextFactory(chat=chat, message=text_message)
        self.assertEqual(str(chat_message), f"{self.user1.email} - (Texto) -> {chat}")


    def test_chatmessage_model_unique_together(self):
        '''
        Description:
            Tests the unique_together of the ChatMessage model.

        Pre-conditions:
            - The ChatMessage model must be correctly defined.

        Post-conditions:
            - The unique_together must be the chat and the message of the chat message.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        text_message = TextMessageFactory(author=self.user1)
        chat_message = ChatMessageTextFactory(chat=chat, message=text_message)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ChatMessageTextFactory(chat=chat, message=text_message)


    def test_chatmessage_model_is_author_method(self):
        '''
        Description:
            Tests the is_author method of the ChatMessage model.

        Pre-conditions:
            - The ChatMessage model must be correctly defined.

        Post-conditions:
            - The is_author method must return True if the user passed is the author of the chat message.
            - The is_author method must return False if the user passed is not the author of the chat message.
        '''
        
        chat = ChatFactory(user1=self.user1, user2=self.user2)
        text_message = TextMessageFactory(author=self.user1)
        chat_message = ChatMessageTextFactory(chat=chat, message=text_message)
        self.assertTrue(chat_message.is_author(self.user1))
        self.assertFalse(chat_message.is_author(self.user2))