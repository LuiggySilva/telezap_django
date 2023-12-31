from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UsernameField

from PIL import Image

User = get_user_model()
MIN_ASPECT_RATIO = 0.75  # Proporção mínima (largura / altura)
MAX_ASPECT_RATIO = 1.75  # Proporção máxima (largura / altura)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
        ]
        labels = {
            'username':'Nick',
            'email':'Email',
        }
        field_classes = {"username": UsernameField}



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'photo',
            'username',
            'status',
            'email',
        ]
        labels = {
            'username':'Nick',
            'email':'Email',
            'status':'Status',
            'photo':'Foto',
        }
        widgets = {
            'status': forms.Textarea(
                attrs={
                    'style': 'width: 100%',
                    'class': 'form-control z-depth-1',
                    'cols': '40',
                    'rows': '10',
                }),
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        
        if photo:
            photo_file = Image.open(photo)
            width, height = photo_file.width, photo_file.height
            aspect_ratio = width / height
            if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
                self.add_error('photo', "A proporção da imagem deve ser aproximadamente quadrada")
        return photo



class UserProfileConfigForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'config_photo_visibility',
            'config_email_visibility',
            'config_status_visibility',
            'config_online_visibility',
        ]
        labels = {
            'config_photo_visibility':'Foto',
            'config_email_visibility':'Email',
            'config_status_visibility':'Status',
            'config_online_visibility':'Online',
        }
        widgets = {
            'config_photo_visibility': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'config_email_visibility': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'config_status_visibility': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'config_online_visibility': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
        }


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

        labels = {
            'username':'Nick',
            'email':'Email',
            'status':'Status',
            'photo':'Foto',
            'config_photo_visibility':'Foto',
            'config_email_visibility':'Email',
            'config_status_visibility':'Status',
            'config_online_visibility':'Online',
        }

    def clean_friends(self):
        friends = self.cleaned_data['friends']
        if self.instance in friends.all():
            self.add_error('friends', "Você não pode adicionar a si mesmo como amigo.")
        return friends

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')

        if photo:
            photo_file = Image.open(photo)
            width, height = photo_file.width, photo_file.height
            aspect_ratio = width / height
            if aspect_ratio < MIN_ASPECT_RATIO or aspect_ratio > MAX_ASPECT_RATIO:
                self.add_error('photo', "A proporção da imagem deve ser aproximadamente quadrada")
        return photo

