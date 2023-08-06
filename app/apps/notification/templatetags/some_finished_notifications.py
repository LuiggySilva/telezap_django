from django.template.defaultfilters import register
from django.utils.safestring import mark_safe
from string import Template

@register.filter(name='some_finished')
def some_finished(notifications, user):
    output = True
    for notification in notifications:
        if notification.is_finished():
            if notificacao.is_author(user):
                if notificacao.author_view:
                    output = False
            else:
                if notificacao.receiver_view:
                    output = False
    return output