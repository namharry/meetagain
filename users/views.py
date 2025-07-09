from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib.auth import authenticate, login
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 회원가입 후 자동 로그인
            return redirect('/')  # 메인 페이지로 이동 (URL 바꾸면 됨)
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        student_id = request.POST['student_id']
        password = request.POST['password']
        user = authenticate(request, student_id=student_id, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')  # 로그인 성공 시 이동할 경로
        else:
            messages.error(request, '아이디 또는 비밀번호가 틀렸습니다.')
    return render(request, 'users/login.html')