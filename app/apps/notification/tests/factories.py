import factory
from apps.user.tests.factories import UserFactory
from apps.notification.models import Notification, FriendshipRequest, GroupRequest


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    author = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    author_view = True
    receiver_view = True
    status = 'P'


class FriendshipRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FriendshipRequest

    author = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    author_view = True
    receiver_view = True
    status = 'P'


class GroupRequestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GroupRequest

    author = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    author_view = True
    receiver_view = True
    status = 'P'
    group = factory.Sequence(lambda n: n)