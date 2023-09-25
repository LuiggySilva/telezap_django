# Generated by Django 4.2.3 on 2023-09-05 19:44

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0006_alter_imagemessage_image'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chat',
            options={'verbose_name': 'Chat', 'verbose_name_plural': 'Chats'},
        ),
        migrations.AlterUniqueTogether(
            name='chat',
            unique_together={('user1', 'user2')},
        ),
    ]