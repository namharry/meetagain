# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(UserCreationForm):
    student_id = forms.CharField(label='학번', max_length=20, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    auth_code = forms.CharField(label='인증번호', max_length=6, required=False)  # ✅ 추가

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
        fields = ("student_id", "email", "auth_code", "password1", "password2")  # ✅ auth_code 포함

    def save(self, commit=True):
        user = super().save(commit=False)
        user.student_id = self.cleaned_data["student_id"]
        user.username = self.cleaned_data["student_id"]  # username 필드는 여전히 필요
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("이미 사용 중인 이메일입니다.")
        return email


class PasswordChangeCustomForm(SetPasswordForm):
    student_id = forms.CharField(label='학번', max_length=20)

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
# ✅ 추가: 인증번호 기반 비밀번호 재설정 폼
class PasswordResetWithCodeForm(forms.Form):
    email = forms.EmailField(label="이메일")
    auth_code = forms.CharField(label="인증번호", max_length=6, required=False)
    new_password = forms.CharField(
        label="새 비밀번호",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False
    )
    confirm_password = forms.CharField(
        label="새 비밀번호 확인",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.step = kwargs.pop('step', 'email')  # default = email
        super().__init__(*args, **kwargs)

        # step에 따라 필수 필드를 다르게 설정
        if self.step == 'code':
            self.fields['auth_code'].required = True
        elif self.step == 'password':
            self.fields['auth_code'].required = True
            self.fields['new_password'].required = True
            self.fields['confirm_password'].required = True

    def clean(self):
        cleaned_data = super().clean()
        if self.step == 'password':
            pw1 = cleaned_data.get("new_password")
            pw2 = cleaned_data.get("confirm_password")
            if pw1 and pw2 and pw1 != pw2:
                raise forms.ValidationError("비밀번호가 일치하지 않습니다.")
        return cleaned_data