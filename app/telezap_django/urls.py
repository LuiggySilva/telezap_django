from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import (
    LoginView, 
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from apps.user.views import SignupView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.user.urls', namespace='user')),
    path('notificacoes/', include('apps.notification.urls', namespace='notification')),
    path('chat/', include('apps.chat.urls', namespace='chat')),
    path('grupo/', include('apps.group_chat.urls', namespace='group_chat')),
    path('chamada-video/', include('apps.videocall.urls', namespace='videocall')),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('recuperar-senha/', PasswordResetView.as_view(), name='reset_password'),
    path('recuperar-senha/email-enviado/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('recuperar-senha/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('recuperar-senha/sucesso/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if (settings.DEBUG):
    urlpatterns = [
        path('__debug__/', include('debug_toolbar.urls')),
    ] + urlpatterns
