# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['student_id', 'username', 'email', 'password1', 'password2']
