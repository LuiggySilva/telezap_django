# Generated by Django 4.2.3 on 2023-08-06 03:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user1_view', models.BooleanField(default=True)),
                ('user2_view', models.BooleanField(default=True)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usuario2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_type', models.CharField(choices=[('T', 'Texto'), ('I', 'Imagem'), ('A', 'Audio'), ('V', 'Video')], editable=False, max_length=1)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Mensagens',
            },
        ),
        migrations.CreateModel(
            name='ImageMessage',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='chat.message')),
                ('image', models.ImageField(upload_to='user_chat_media')),
            ],
            options={
                'verbose_name': 'Mensagem de Imagem',
                'verbose_name_plural': 'Mensagens de Imagem',
            },
            bases=('chat.message',),
        ),
        migrations.CreateModel(
            name='TextMessage',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='chat.message')),
                ('text', models.TextField()),
            ],
            options={
                'verbose_name': 'Mensagem de Texto',
                'verbose_name_plural': 'Mensagens de Texto',
            },
            bases=('chat.message',),
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visualized', models.BooleanField(default=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='chat.chat')),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='chat.message')),
            ],
            options={
                'verbose_name': 'Mensagem de Chat',
                'verbose_name_plural': 'Mensagens de Chats',
                'unique_together': {('chat', 'message')},
            },
        ),
    ]