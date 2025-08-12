# backend/users/views.py
from django.conf import settings
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
from django.core.paginator import Paginator

# ✅ 추가: 설정 업데이트용 데코레이터
from django.views.decorators.http import require_POST
import json

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
                backend_path = settings.AUTHENTICATION_BACKENDS[0]  # settings.py 첫 번째 인증 백엔드 가져오기
                user.backend = backend_path  # user 객체에 backend 속성 추가

                login(request, user, backend=backend_path)  # login() 함수 호출 시 backend 인자도 넘김

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
            request.session['reset_step'] = 'password'
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
    return redirect('users:login')


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
    """
    비밀번호 재설정(이메일 → 코드 → 새 비번) 뷰.
    - GET 진입 시 단계 초기화(항상 email 단계부터 시작)
    - 코드 검증은 AJAX 또는 폼 submit 모두 지원
    - 비번 변경 후에는 authenticate() → login() 순으로 자동 로그인
    """
    # 0) GET으로 들어오면 항상 초기화 (원치 않으면 이 블록 제거)
    if request.method == 'GET':
        for k in ('reset_step', 'reset_email', 'reset_verified_email'):
            request.session.pop(k, None)

    step = request.session.get('reset_step', 'email')

    if request.method == 'POST':
        # 1) 인증번호 전송
        if 'send_code' in request.POST:
            form = PasswordResetWithCodeForm(request.POST, step='email')
            if form.is_valid():
                email = form.cleaned_data['email'].strip().lower()
                if not User.objects.filter(email=email).exists():
                    form.add_error('email', "등록되지 않은 이메일입니다.")
                    step = 'email'
                else:
                    send_auth_code(email, purpose="reset")
                    request.session['reset_email'] = email
                    request.session['reset_step'] = 'code'
                    step = 'code'
                    messages.info(request, "인증번호가 이메일로 전송되었습니다.")
            else:
                step = 'email'

        # 2) (옵션) 폼 submit으로 코드 검증하는 흐름
        elif 'verify_code' in request.POST:
            form = PasswordResetWithCodeForm(request.POST, step='code')
            email = request.session.get('reset_email')
            if form.is_valid():
                code = form.cleaned_data['auth_code']
                if email and verify_auth_code(email, code, purpose="reset"):
                    request.session['reset_verified_email'] = email
                    request.session['reset_step'] = 'password'
                    step = 'password'
                    messages.success(request, "인증이 완료되었습니다. 새 비밀번호를 입력하세요.")
                else:
                    form.add_error('auth_code', "인증번호가 올바르지 않거나 만료되었습니다.")
                    step = 'code'
            else:
                step = 'code'

        # 3) 새 비밀번호 설정
        elif 'reset_password' in request.POST:
            form = PasswordResetWithCodeForm(request.POST, step='password')
            email = request.session.get('reset_verified_email')
            if form.is_valid():
                if not email:
                    messages.error(request, "인증 절차를 먼저 완료해주세요.")
                    return redirect('users:password_reset')
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    messages.error(request, "등록되지 않은 이메일입니다.")
                    return redirect('users:password_reset')

                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()

                # ✅ 여러 인증 백엔드 대응: 가능한 조합으로 차례대로 시도
                auth_user = (
                    authenticate(request, student_id=getattr(user, 'student_id', None), password=new_password)
                    or authenticate(request, username=getattr(user, 'student_id', None), password=new_password)
                    or authenticate(request, email=user.email, password=new_password)
                )

                if auth_user is not None:
                    login(request, auth_user)
                else:
                    messages.warning(request, "비밀번호는 변경됐지만 자동 로그인에 실패했습니다. 다시 로그인해 주세요.")
                    for k in ('reset_email', 'reset_verified_email', 'reset_step'):
                        request.session.pop(k, None)
                    return redirect('users:login')

                messages.success(request, "비밀번호가 재설정되었습니다.")
                for k in ('reset_email', 'reset_verified_email', 'reset_step'):
                    request.session.pop(k, None)
                return redirect('users:login')  
            else:
                step = 'password'

        else:
            # 알 수 없는 submit → 현재 단계 폼으로 재표시
            form = PasswordResetWithCodeForm(step=step)

    else:
        # GET: 현재 단계 폼
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

@login_required
def mypage_view(request):
    if request.method == 'POST':
        user = request.user
        user.allow_notification = 'allow_notification' in request.POST
        user.allow_location = 'allow_location' in request.POST
        user.save(update_fields=['allow_notification', 'allow_location'])
        return redirect('users:mypage')

    # ✅ 내가 습득한 물건
    f_qs = FoundItem.objects.filter(user=request.user).order_by('-id')
    f_page = Paginator(f_qs, 10).get_page(request.GET.get('page'))
    f_items = list(f_page.object_list)
    for obj in f_items:
        if not getattr(obj, "title", None):
            obj.title = obj.name

    # ✅ 내가 잃어버린 물건
    l_qs = LostItem.objects.filter(user=request.user).order_by('-id')
    l_page = Paginator(l_qs, 10).get_page(request.GET.get('lost_page'))
    l_items = list(l_page.object_list)
    for obj in l_items:
        if not getattr(obj, "title", None):
            obj.title = obj.name

    return render(request, 'mypage/mypage.html', {
        'found_items': f_items,
        'page_obj': f_page,        # 템플릿에서 페이지네이션 쓰면 그대로 동작
        'found_count': f_qs.count(),
        'tab': 'found',            # 템플릿에 탭 조건 있으면 유지
        'lost_items': l_items,
        'lost_page_obj': l_page,
        'lost_count': l_qs.count(),
    })

# ✅ 수정 완료: 설정 업데이트 API (mypage 토글이 호출)
@login_required
@require_POST
def update_setting(request):
    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "invalid json"}, status=400)

    setting = data.get("setting")
    value = bool(data.get("value"))

    # 프론트에서 오는 키 -> User 모델 필드 매핑
    mapping = {
        "notification": "allow_notification",
        "location": "allow_location",
    }
    field = mapping.get(setting)
    if not field:
        return JsonResponse({"ok": False, "error": "invalid setting"}, status=400)

    # 실제 User 모델에 필드가 있는지 확인
    if not hasattr(request.user, field):
        return JsonResponse({"ok": False, "error": f"missing field {field}"}, status=400)

    setattr(request.user, field, value)
    request.user.save(update_fields=[field])

    return JsonResponse({
        "ok": True,
        "field": field,
        "value": getattr(request.user, field),
    })

def app_settings_view(request): return HttpResponse("앱 설정 - 준비 중입니다.")
def found_items_view(request): return HttpResponse("습득물 등록 내역 - 준비 중입니다.")
def lost_items_view(request): return HttpResponse("분실물 등록 내역 - 준비 중입니다.")

@admin_required
def admin_lost_list(request):
    lost_items = LostItem.objects.all().order_by('-created_at')
    return render(request, 'users/admin_lost_list.html', {'lost_items': lost_items})

@admin_required
def admin_found_list(request):
    found_items = FoundItem.objects.all().order_by('-created_at')
    return render(request, 'users/admin_found_list.html', {'found_items': found_items})
