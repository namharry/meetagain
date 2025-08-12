"""
Django settings for config project.
"""

from pathlib import Path
from django.contrib.messages import constants as messages
import os
import cloudinary  # ← 추가

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

    # --- Cloudinary ---
    'cloudinary',
    'cloudinary_storage',

    # --- 기존 앱 ---
    'users',
    'meetagain',
]

# === 템플릿 ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR.parent / 'frontend' / 'templates',
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
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
        'NAME': 'railway',
        'USER': 'postgres',
        'PASSWORD': 'lwrWbOfFBKqFCiVAGvJncqGekcbsqIYp',
        'HOST': 'yamabiko.proxy.rlwy.net',
        'PORT': '26651',
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
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# === 정적/미디어 ===
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend' / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ✅ Cloudinary 저장소 설정 (django-cloudinary-storage용)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'dr4kqw4vg',
    'API_KEY': '679437386832466',
    'API_SECRET': 'LxageC_itSH7aeezXmSP3shxyWg',
}

# ✅ Django 5 권장 방식(STORAGES) + 하위호환(DEFAULT_FILE_STORAGE) 동시에 지정
STORAGES = {
    'default': {'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

MEDIA_URL = '/media/'
# MEDIA_ROOT = BASE_DIR / 'media'  # Cloudinary 사용 시 실사용 안 함. 헷갈리면 주석 유지

# ✅ cloudinary-python에도 명시적으로 구성 값 주입 (쉘에서 cloudinary.config().cloud_name=None 문제 방지)
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True,
)

# === 사용자/인증 ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.User'

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

# === 이메일 ===
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'meetagain.noreply@gmail.com'
EMAIL_HOST_PASSWORD = 'urxa itwv vwji swpl'  # 실제로는 환경변수로 분리 권장
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
