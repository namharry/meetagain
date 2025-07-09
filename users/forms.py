# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User

class SignupForm(UserCreationForm):
    studentid = forms.CharField(label='학번', max_length=30)

    password1 = forms.CharField(
        label='비밀번호 입력',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=''
    )

    password2 = forms.CharField(
        label='비밀번호 재입력',
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='비밀번호: 8~16자의 영문, 숫자, 특수문자를 사용해주세요.'
    )

    class Meta:
        model = User
        fields = ("studentid", "username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = ''

class PasswordChangeCustomForm(SetPasswordForm):
    studentid = forms.CharField(label='학번', max_length=30)

    new_password1 = forms.CharField(
        label="새 비밀번호 입력",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=''
    )
    new_password2 = forms.CharField(
        label="새 비밀번호 재입력",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text='비밀번호: 8~16자의 영문, 숫자, 특수문자를 사용해주세요.'
    )
