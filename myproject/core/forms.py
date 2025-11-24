from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import *
import random
from django.utils import timezone
from datetime import timedelta
from django_ckeditor_5.widgets import CKEditor5Widget


class AdvertisementForm(forms.ModelForm):
    """
    Форма создания/редактирования объявления
    """
    class Meta:
        model = Advertisement
        fields = ['title', 'content', 'category']
        widgets = {
            'content': CKEditor5Widget(
                attrs={'class': 'django_ckeditor_5'},
                config_name='extends'
            ),
            'category': forms.Select(choices=Category.choices), 
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False


class RegistrationForm(UserCreationForm):
    """
    Форма регистрации пользователя
    """
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.verification_code = ''.join(random.choices('0123456789', k=6))
        user.verification_code_expires = timezone.now() + timedelta(minutes=10)
        if commit:
            user.save()  
        return user

class VerificationForm(forms.Form):
    """
    Форма верификации пользователя
    """
    code = forms.CharField(max_length=6, label='Код подтверждения')


class LoginForm(AuthenticationForm):
    """
    Форма лоигна пользователей
    """
    username = forms.EmailField(label='Email', max_length=256)

    class Meta: 
        fields = ['username', 'password']

class ResponseForm(forms.ModelForm):
    """
    Форма откликов на объявление
    """
    class Meta:
        model = Response
        fields = ['text']
        widgets = {'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отклик...'})}