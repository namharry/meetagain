# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import SignupForm

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('login')  # 변경 후 로그인 페이지로 이동

# 로그인 뷰
def login_view(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        user = authenticate(request, username=student_id, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, '학번 또는 비밀번호가 잘못되었습니다.')
    return render(request, 'users/login.html')


# 비밀번호 변경 뷰
def password_change_view(request):
    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 != new_password2:
            messages.error(request, '비밀번호가 일치하지 않습니다.')
        else:
            user = request.user
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)  # 비밀번호 변경 후 자동 로그인 유지
            messages.success(request, '비밀번호가 변경되었습니다.')
            return redirect('login')
    return render(request, 'users/password_change.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 가입 직후 로그인
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('login')  # 로그인 페이지로 리디렉션
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})