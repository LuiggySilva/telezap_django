from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    author = models.ForeignKey(User, related_name="autores", on_delete=models.CASCADE, verbose_name='Autor')
    receiver = models.ForeignKey(User, related_name="recebedores", on_delete=models.CASCADE, verbose_name='Recebedor')
    author_view = models.BooleanField(default=True, verbose_name='Visualização do autor')
    receiver_view = models.BooleanField(default=True, verbose_name='Visualização do recebedor')
    date = models.DateField(auto_now_add=True, verbose_name='Data')
    
    status_choices = (
        ('P', 'Pendente'),
        ('A', 'Aceito'),
        ('R', 'Recusado'),
    )
    status = models.CharField(max_length=1, choices=status_choices, default=status_choices[0], verbose_name='Status')

    def __str__(self):
        return f"{self.author.email} -> {self.receiver.email}"

    def is_author(self, user):
        return self.author == user

    def is_finished(self):
        return self.status != 'P'


class FriendshipRequest(Notification):
    notification_type = models.CharField(max_length=1, default='A', editable=False, verbose_name='Tipo')

    class Meta:
        verbose_name = "Solicitação de amizade"
        verbose_name_plural = "Solicitações de amizade"


class GroupRequest(Notification):
    notification_type = models.CharField(max_length=1, default='G', editable=False, verbose_name='Tipo')
    #TODO: Alterar quando criar o model de grupo
    group = models.IntegerField(verbose_name='Grupo')

    class Meta:
        verbose_name = "Solicitação de grupo"
        verbose_name_plural = "Solicitações de grupo"



