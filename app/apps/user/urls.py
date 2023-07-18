from django.urls import path, include
from . import views

app_name = 'user'

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing_page'),
    path('perfil/<slug:slug>/', views.UserProfileView.as_view(), name="profile"),
    path('perfil/<slug:slug>/atualizar-perfil', views.profile_update, name="profile_update"),
    path('perfil/<slug:slug>/atualizar-senha', views.profile_password_update, name="profile_password_update"),
    path('perfil/<slug:slug>/atualizar-configuracoes', views.profile_config_update, name="profile_config_update"),
]