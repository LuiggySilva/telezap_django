# Generated by Django 4.2.3 on 2023-08-09 15:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_chat_user1_alter_chat_user1_view_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='date',
        ),
        migrations.AddField(
            model_name='message',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Data'),
            preserve_default=False,
        ),
    ]
