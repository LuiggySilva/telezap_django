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
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_view', models.BooleanField(default=True)),
                ('receiver_view', models.BooleanField(default=True)),
                ('date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[('P', 'Pendente'), ('A', 'Aceito'), ('R', 'Recusado')], default=('P', 'Pendente'), max_length=1)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='autores', to=settings.AUTH_USER_MODEL)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recebedores', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FriendshipRequest',
            fields=[
                ('notification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='notification.notification')),
                ('notification_type', models.CharField(default='A', editable=False, max_length=1)),
            ],
            options={
                'verbose_name': 'Solicitação de amizade',
                'verbose_name_plural': 'Solicitações de amizade',
            },
            bases=('notification.notification',),
        ),
        migrations.CreateModel(
            name='GroupRequest',
            fields=[
                ('notification_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='notification.notification')),
                ('notification_type', models.CharField(default='B', editable=False, max_length=1)),
                ('group', models.IntegerField()),
            ],
            options={
                'verbose_name': 'Solicitação de grupo',
                'verbose_name_plural': 'Solicitações de grupo',
            },
            bases=('notification.notification',),
        ),
    ]
