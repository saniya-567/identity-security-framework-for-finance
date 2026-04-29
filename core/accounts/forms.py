from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django import forms

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        help_text="",  # remove default
        widget=forms.TextInput(attrs={'placeholder': 'Enter username'})
    )

    password1 = forms.CharField(
        help_text="",
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'})
    )

    password2 = forms.CharField(
        help_text="",
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'password1', 'password2']

        