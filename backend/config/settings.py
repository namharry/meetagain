"""
Django settings for config project.
"""

from pathlib import Path
from django.contrib.messages import constants as messages
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# === 기본 ===
SECRET_KEY = 'django-insecure-o+*ot4wz0-gf&^xqduqfx#sc&-g@7iat)8#+!)9a@id=wy^&o*'
DEBUG = True
ALLOWED_HOSTS = []

# === 앱 ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'meetagain',
]

# === 템플릿 ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.parent / 'frontend' / 'templates',  # ← (OK) frontend 템플릿
            BASE_DIR / 'templates',                      # ← (필요 없으면 지워도 무방)
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # ← base.html의 request.path 위해 필수
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === 미들웨어 ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

# === DB ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'meetagain'),
        'USER': os.getenv('DB_USER', 'meetagain'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'meetagainpw'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),  # 같은 PC면 이대로, 팀원이면 DB 띄운 PC의 IP
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# === 패스워드 ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# === i18n ===
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'   # ← 변경
USE_I18N = True
USE_TZ = True

# === 정적/미디어 ===
STATIC_URL = '/static/'    # ← 슬래시 포함
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend' / 'static',  # ← frontend/static 사용
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# === 사용자/인증 ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # ← 중복 정리
AUTH_USER_MODEL = 'users.User'                        # ← 중복 정리

AUTHENTICATION_BACKENDS = [
    'users.backends.StudentIDBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/meetagain/'

# === 메시지 ===
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

# === 이메일 (개발용: 환경변수로 분리 권장) ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'meetagain.noreply@gmail.com'
EMAIL_HOST_PASSWORD = 'urxa itwv vwji swpl'  # ← 앱 비밀번호: 환경변수로 빼는 걸 강력 권장
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
