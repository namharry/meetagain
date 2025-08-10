from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import SignupForm, PasswordChangeCustomForm, PasswordResetWithCodeForm
from meetagain.models import LostItem, FoundItem
from django.contrib.auth.hashers import make_password
from .services import send_auth_code, verify_auth_code

User = get_user_model()

# ------------------------------
# ✅ 회원가입 전 이메일 인증 검사 포함
# ------------------------------
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            print("폼 유효성 검사 통과")
            email = form.cleaned_data.get("email")
            verified_email = request.session.get("signup_verified_email")
            print(f"인증된 이메일: {verified_email}, 입력된 이메일: {email}")
            if verified_email != email:
                form.add_error(None, "이메일 인증을 완료해주세요.")
            elif User.objects.filter(email=email).exists():
                form.add_error("email", "이미 사용 중인 이메일입니다.")
            else:
                user = form.save(commit=False)
                user.email = email
                user.save()
                backend_path = 'django.contrib.auth.backends.ModelBackend'  # 기본 인증 백엔드 경로, settings.py에 따라 다를 수 있음
                user.backend = backend_path

                login(request, user)
                print("유저 저장 완료")
                messages.success(request, '회원가입이 완료되었습니다.')
                request.session.pop("signup_verified_email", None)
                return redirect('users:login')
        else:
            print("폼 유효성 검사 실패")
            print(form.errors)
    else:
        form = SignupForm()
    return render(request, 'auth/signup.html', {'form': form})

@csrf_exempt
def send_signup_code_ajax(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            send_auth_code(email, purpose='signup')
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def verify_signup_code_ajax(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        print(">>> 이메일:", email)
        print(">>> 입력한 코드:", code)

        if verify_auth_code(email, code, purpose='signup'):
            print(">>> 인증 성공")
            request.session['signup_verified_email'] = email
            return JsonResponse({'success': True})
        else:
            print(">>> 인증 실패")
    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def verify_reset_code_ajax(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        code = request.POST.get('code')
        if verify_auth_code(email, code, purpose='reset'):
            request.session['reset_verified_email'] = email
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

# ------------------------------
# 🔐 로그인
# ------------------------------
def login_view(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')  # 로그인 폼 input name에 맞게
        password = request.POST.get('password')

        user = authenticate(request, student_id=student_id, password=password)

        if user is not None:
            login(request, user)
            return redirect('meetagain:index')
        else:
            messages.error(request, '학번 또는 비밀번호가 잘못되었습니다.')

    return render(request, 'auth/login.html')



# ------------------------------
# 🔐 로그아웃
# ------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "로그아웃되었습니다.")
    return redirect('login')

# ------------------------------
# 🔐 비밀번호 변경 (로그인 상태)
# ------------------------------
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
            update_session_auth_hash(request, user)
            messages.success(request, '비밀번호가 변경되었습니다.')
            return redirect('users:login')
    return render(request, 'auth/reset_password.html')

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:login')

# ------------------------------
# 🔐 비밀번호 재설정 (이메일 인증 기반)
# ------------------------------
def custom_password_reset_view(request):
    step = request.session.get('reset_step', 'email')
    verified_email = request.session.get('reset_verified_email')

    # 1단계: 이메일 입력 및 인증번호 전송
    if 'send_code' in request.POST:
        form = PasswordResetWithCodeForm(request.POST, step='email')
        if form.is_valid():
            email = form.cleaned_data['email']
            if not User.objects.filter(email=email).exists():
                form.add_error('email', "등록되지 않은 이메일입니다.")
                step = 'email'
            else:
                send_auth_code(email, purpose="reset")
                request.session['reset_step'] = 'code'
                request.session['reset_email'] = email
                step = 'code'
                messages.info(request, "인증번호가 이메일로 전송되었습니다.")
        else:
            step = 'email'

    # 2단계: 인증번호 확인
    elif 'verify_code' in request.POST:
        form = PasswordResetWithCodeForm(request.POST, step='code')
        email = request.session.get('reset_email')
        if form.is_valid():
            code = form.cleaned_data['auth_code']
            if email and verify_auth_code(email, code, purpose="reset"):
                request.session['reset_step'] = 'password'
                request.session['reset_verified_email'] = email
                step = 'password'
                messages.success(request, "인증이 완료되었습니다. 새 비밀번호를 입력하세요.")
            else:
                form.add_error('auth_code', "인증번호가 올바르지 않거나 만료되었습니다.")
                step = 'code'
        else:
            step = 'code'

    # 3단계: 새 비밀번호 설정 + 자동 로그인
    elif 'reset_password' in request.POST:
        form = PasswordResetWithCodeForm(request.POST, step='password')
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            email = verified_email  # 세션에 저장된 인증된 이메일만 사용
            if not email:
                messages.error(request, "인증 절차를 먼저 완료해주세요.")
                return redirect('users:password_reset')
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                # 인증 완료 후 자동 로그인
                login(request, user)
                messages.success(request, "비밀번호가 재설정되었습니다.")
                # 비밀번호 변경 완료 후 세션 정리
                request.session.pop('reset_email', None)
                request.session.pop('reset_verified_email', None)
                request.session.pop('reset_step', None)
                return redirect('users:login') 
            except User.DoesNotExist:
                form.add_error('email', "등록되지 않은 이메일입니다.")
                step = 'password'
        else:
            step = 'password'

    # GET 요청 또는 초기 화면
    else:
        form = PasswordResetWithCodeForm(step=step)

    return render(request, 'auth/reset_password.html', {
        'form': form,
        'step': step,
    })

# ------------------------------
# 👤 마이페이지 및 더미 뷰들
# ------------------------------
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)

def dummy_view(request):
    return HttpResponse("준비 중인 기능입니다.")

def my_account_view(request):
    dummy_user = {
        'email': 'sungshin@ac.kr',
        'name': '김성신',
        'student_id': '20230001',
        'profile_pic_url': 'https://via.placeholder.com/100'
    }
    return render(request, 'users/my_account.html', {'user': dummy_user})

def app_settings_view(request): return HttpResponse("앱 설정 - 준비 중입니다.")
def found_items_view(request): return HttpResponse("습득물 등록 내역 - 준비 중입니다.")
def lost_items_view(request): return HttpResponse("분실물 등록 내역 - 준비 중입니다.")
def quit_view(request): return HttpResponse("탈퇴 - 준비 중입니다.")
def customer_center_view(request): return HttpResponse("고객센터 - 준비 중입니다.")
def inquiry_view(request): return HttpResponse("문의 - 준비 중입니다.")
def notice_view(request): return HttpResponse("공지사항 - 준비 중입니다.")
def faq_view(request): return HttpResponse("FAQ - 준비 중입니다.")
def guide_view(request): return HttpResponse("이용안내 - 준비 중입니다.")

@admin_required
def admin_lost_list(request):
    lost_items = LostItem.objects.all().order_by('-created_at')
    return render(request, 'users/admin_lost_list.html', {'lost_items': lost_items})

@admin_required
def admin_found_list(request):
    found_items = FoundItem.objects.all().order_by('-created_at')
    return render(request, 'users/admin_found_list.html', {'found_items': found_items})