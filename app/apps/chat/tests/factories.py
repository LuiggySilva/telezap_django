import factory
from apps.user.tests.factories import UserFactory
from apps.chat.models import Chat, ChatMessage, TextMessage, ImageMessage


class TextMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TextMessage

    author = factory.SubFactory(UserFactory)
    message_type = 'T'
    text = factory.Sequence(lambda n: f'Text Message {n}')



class ImageMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImageMessage

    author = factory.SubFactory(UserFactory)
    message_type = 'I'
    image = factory.django.ImageField(color='blue')



class ChatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Chat

    user1 = factory.SubFactory(UserFactory)
    user2 = factory.SubFactory(UserFactory)
    user1_view = True
    user2_view = True



class ChatMessageTextFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatMessage

    chat = factory.SubFactory(ChatFactory)
    message = factory.SubFactory(TextMessageFactory)
    visualized = False



class ChatMessageImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChatMessage

    chat = factory.SubFactory(ChatFactory)
    message = factory.SubFactory(ImageMessageFactory)
    visualized = False