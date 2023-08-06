from django.test import TestCase
from .factories import UserFactory, NotificationFactory, FriendshipRequestFactory, GroupRequestFactory
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class NotificationTest(TestCase):
    def setUp(self):
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

    
    def test_notification_model_str_method(self):
        '''
        Description:
            Tests the __str__ method of the Notification model.

        Pre-conditions:
            - The Notification model must be correctly defined.

        Post-conditions:
            - The __str__ method must return the author and the receiver of the notification.
        '''
        
        notification = NotificationFactory(author=self.user1, receiver=self.user2)
        self.assertEqual(str(notification), f"{self.user1} -> {self.user2}")


    def test_notification_model_default_status(self):
        '''
        Description:
            Tests the default status of the Notification model.

        Pre-conditions:
            - The Notification model must be correctly defined.

        Post-conditions:
            - The default status must be 'P' (pending).
        '''

        notification = NotificationFactory(author=self.user1, receiver=self.user2)
        self.assertEqual(notification.status, 'P')


    def test_notification_model_is_author_method(self):
        '''
        Description:
            Tests the is_author method of the Notification model.

        Pre-conditions:
            - The Notification model must be correctly defined.

        Post-conditions:
            - The is_author method must return True if the user passed is the author of the notification.
            - The is_author method must return False if the user passed is not the author of the notification.
        '''
        
        notification = NotificationFactory(author=self.user1, receiver=self.user2)
        self.assertTrue(notification.is_author(self.user1))
        self.assertFalse(notification.is_author(self.user2))


    def test_notification_model_is_finished_method(self):
        '''
        Description:
            Tests the is_finished method of the Notification model.

        Pre-conditions:
            - The Notification model must be correctly defined.

        Post-conditions:
            - The is_finished method must return True if the status of the notification is different from 'P' (pending).
            - The is_finished method must return False if the status of the notification is equal to 'P' (pending).
        '''
        
        notification = NotificationFactory(author=self.user1, receiver=self.user2)
        self.assertFalse(notification.is_finished())
        notification.status = 'A'
        self.assertTrue(notification.is_finished())
        notification.status = 'R'
        self.assertTrue(notification.is_finished())


    def test_notification_model_default_visualization_values(self):
        '''
        Description:
            Tests the default author and receiver visualization values of the Notification model.

        Pre-conditions:
            - The Notification model must be correctly defined.

        Post-conditions:
            - The default author and receiver visualization values must be True.
        '''
        
        notification = NotificationFactory(author=self.user1, receiver=self.user2)
        self.assertTrue(notification.author_view)
        self.assertTrue(notification.receiver_view)


class FriendshipRequestTest(TestCase):
    def setUp(self):
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
        self.notification = FriendshipRequestFactory(author=self.user1, receiver=self.user2)

    
    def test_friendship_type(self):
        '''
        Description:
            Tests the type of the FriendshipRequest model.

        Pre-conditions:
            - The FriendshipRequest model must be correctly defined.

        Post-conditions:
            - The type must be 'A' (friendship).
        '''
        
        self.assertEqual(self.notification.notification_type, 'A')


class GroupRequestTest(TestCase):
    def setUp(self):
        self.user1_data = {
            'username': 'user1',
            'password': 'User1@123'
        }
        self.user2_data = {
            'username': 'user2',
            'password': 'User2@123'
        }
        #TODO: Atualizar quando criar o model de grupo
        self.group = 10
        self.user1 = UserFactory(**self.user1_data)
        self.user2 = UserFactory(**self.user2_data)
        self.notification = GroupRequestFactory(author=self.user1, receiver=self.user2, group=self.group)

    
    def test_grouprequest_type(self):
        '''
        Description:
            Tests the type of the GroupRequest model.

        Pre-conditions:
            - The GroupRequest model must be correctly defined.

        Post-conditions:
            - The type must be 'G' (group request).
        '''

        self.assertEqual(self.notification.notification_type, 'G')


    #TODO: Atualizar quando criar o model de grupo
    def test_grouprequest_group(self):
        '''
        Description:
            Tests the group of the GroupRequest model.

        Pre-conditions:
            - The GroupRequest model must be correctly defined.

        Post-conditions:
            - The group must be equal to the group passed in the notification creation.
        '''
        
        self.assertEqual(self.notification.group, self.group)
