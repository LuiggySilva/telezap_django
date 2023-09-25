from django.template.defaultfilters import register
from django.utils.safestring import mark_safe
from string import Template

@register.filter(name='some_finished')
def some_finished(notifications, user):
    '''
    Filter that checks if some notification of the user is finished.
    '''

    output = True
    for notification in notifications:
        if notification.is_finished():
            # Verify if the notification is visible to the user
            if notificacao.is_author(user):
                if notificacao.author_view:
                    output = False
            else:
                if notificacao.receiver_view:
                    output = False
    return output