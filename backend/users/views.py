# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .forms import SignupForm
from django.contrib.auth import logout
from django.http import HttpResponse

User = get_user_model()

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('login')  # 변경 후 로그인 페이지로 이동

# 로그인 뷰
def login_view(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        password = request.POST.get('password')
        user = authenticate(request, student_id=student_id, password=password)
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
            user = form.save(commit=False) #user 객체 사용
            user.save() #명시적으로 저장
            login(request, user)  # 가입 직후 로그인
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('login')  # 로그인 페이지로 리디렉션
    else:
        form = SignupForm()
    return render(request, 'users/signup.html', {'form': form})

#로그아웃
def logout_view(request):
    logout(request)
    messages.success(request, "로그아웃되었습니다.")
    return redirect('login')

#dummy page
def dummy_view(request):
    return HttpResponse("준비 중인 기능입니다.")

def my_account_view(request):
    dummy_user = {
        'email': 'sungshin@ac.kr',
        'name': '김성신',
        'student_id': '20230001',
        'profile_pic_url': 'https://via.placeholder.com/100'  # 임시 이미지
    }
    return render(request, 'users/my_account.html', {'user': dummy_user})

def app_settings_view(request):
    return HttpResponse("앱 설정 (알림 온오프, 위치정보 동의 설정) - 준비 중입니다.")

def found_items_view(request):
    return HttpResponse("습득물 등록 내역 - 준비 중입니다.")

def lost_items_view(request):
    return HttpResponse("분실물 등록 내역 - 준비 중입니다.")

def quit_view(request):
    return HttpResponse("탈퇴 - 준비 중입니다.")

def customer_center_view(request):
    return HttpResponse("고객센터 - 준비 중입니다.")

def inquiry_view(request):
    return HttpResponse("관리자에게 문의 - 준비 중입니다.")

def notice_view(request):
    return HttpResponse("공지사항 - 준비 중입니다.")

def faq_view(request):
    return HttpResponse("FAQ - 준비 중입니다.")

def guide_view(request):
    return HttpResponse("이용안내 - 준비 중입니다.")

# admin_views.py
from django.contrib.auth.decorators import user_passes_test
from items.models import LostItem, FoundItem  # 분실물/습득물 모델 import 필요

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

@admin_required
def admin_lost_list(request):
    lost_items = LostItem.objects.all().order_by('-created_at')
    return render(request, 'users/admin_lost_list.html', {'lost_items': lost_items})

@admin_required
def admin_found_list(request):
    found_items = FoundItem.objects.all().order_by('-created_at')
    return render(request, 'users/admin_found_list.html', {'found_items': found_items})