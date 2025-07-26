# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(UserCreationForm):
    student_id = forms.CharField(label='학번', max_length=30)

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
        fields = ("student_id", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.student_id = self.cleaned_data["student_id"]
        user.username = self.cleaned_data["student_id"]  # username 필드는 여전히 필요
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user 

class PasswordChangeCustomForm(SetPasswordForm):
    student_id = forms.CharField(label='학번', max_length=30)

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
"""
    def clean_student_id(self):
        student_id = self.cleaned_data.get("student_id")
        if self.user.student_id != student_id:
            raise forms.ValidationError("학번이 일치하지 않습니다.")
        return student_id #학번 재입력을 통한 추가 인증 필요하면 할 것!
        
"""
