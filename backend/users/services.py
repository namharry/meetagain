import random
from django.core.mail import send_mail
from django.core.cache import cache

def generate_auth_code():
    return str(random.randint(100000, 999999))


# ✅ 목적별 인증번호 전송
def send_auth_code(email, purpose='signup'):
    code = generate_auth_code()
    cache.set(f'auth_code_{purpose}_{email}', code, timeout=180)  # key에 목적 포함

    if purpose == 'signup':
        subject = '[MeetAgain] 회원가입 인증번호'
        message = f'회원가입을 위한 인증번호는 {code}입니다.\n3분 안에 입력해 주세요.'
    elif purpose == 'reset':
        subject = '[MeetAgain] 비밀번호 재설정 인증번호'
        message = f'비밀번호 재설정을 위한 인증번호는 {code}입니다.\n3분 안에 입력해 주세요.'
    else:
        subject = '[MeetAgain] 인증번호'
        message = f'인증번호는 {code}입니다.\n3분 안에 입력해 주세요.'

    send_mail(
        subject=subject,
        message=message,
        from_email='meetagain.noreply@gmail.com',
        recipient_list=[email],
        fail_silently=False,
    )


# ✅ 인증번호 검증 (성공 시 삭제)
def verify_auth_code(email, code, purpose='signup'):
    saved_code = cache.get(f'auth_code_{purpose}_{email}')
    if saved_code == code:
        cache.delete(f'auth_code_{purpose}_{email}')
        return True
    return False
