from pathlib import Path

# 프로젝트 최상위 폴더 경로
BASE_DIR = Path(__file__).resolve().parent.parent

# 보안키 (진짜 서비스 땐 숨겨야 함)
SECRET_KEY = 'django-insecure-o+*ot4wz0-gf&^xqduqfx#sc&-g@7iat)8#+!)9a@id=wy^&o*'

DEBUG = True  # 개발중엔 True, 배포할 땐 False로

ALLOWED_HOSTS = []  # 허용할 도메인 리스트, 개발중이라 비워둠

# 설치한 앱들 (내가 만든 앱도 여기 넣어야 함)
INSTALLED_APPS = [
    'django.contrib.admin',     # 관리자 페이지
    'django.contrib.auth',      # 인증 관련
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',                   # 사용자 관련 앱
    'meetagain',               # 메인 앱
]

# 템플릿 설정 (HTML 파일 위치)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.parent / 'frontend' / 'templates',  # frontend/templates 폴더
            BASE_DIR / 'templates',                      # backend/templates 폴더 (필요시)
        ],
        'APP_DIRS': True,  # 앱 내 templates 폴더도 자동 검색
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # request 객체를 템플릿에 전달
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE = [  # 요청-응답 과정에 끼어드는 기능들
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF 공격 방지
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 로그인 사용자 정보 처리
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'  # URL 설정 파일 위치

WSGI_APPLICATION = 'config.wsgi.application'  # WSGI 실행 파일 위치

# 데이터베이스 (여기선 SQLite 사용)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 비밀번호 검증 설정
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# 언어 및 시간대
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 정적 파일 URL
STATIC_URL = 'static/'

# 미디어(업로드 파일) 경로
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 커스텀 유저 모델 지정
AUTH_USER_MODEL = 'users.User'

# 이메일 서버 설정 (Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'meetagain.noreply@gmail.com'  # 보내는 이메일 주소
EMAIL_HOST_PASSWORD = 'urxa itwv vwji swpl'     # 앱 비밀번호 (실제론 숨겨야 함)
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# 로그인 관련 URL
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/meetagain/'

# 메시지 프레임워크 저장소 & 태그
from django.contrib.messages import constants as messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# 인증 백엔드 (학번 인증 + 기본 인증)
AUTHENTICATION_BACKENDS = [
    'users.backends.StudentIDBackend',  # 학번으로 로그인하는 커스텀 백엔드
    'django.contrib.auth.backends.ModelBackend',  # 기본 username 인증 백엔드
]
