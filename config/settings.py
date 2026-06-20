import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-only-change-in-production')
DEBUG = os.environ.get('DEBUG', 'true').lower() in ('1', 'true', 'yes')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop',
]

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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# PostgreSQL via DATABASE_URL, fallback to SQLite for quick local dev
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres'):
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'jalaram'),
            'USER': os.environ.get('POSTGRES_USER', 'postgres'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'pass'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
            'OPTIONS': {
                'connect_timeout': 5,
            },
        }
    }
    if os.environ.get('USE_SQLITE', '').lower() in ('1', 'true', 'yes'):
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-in'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/assets/'
STATICFILES_DIRS = [BASE_DIR / 'public' / 'assets']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Serve public/data and other public root files
PUBLIC_DIR = BASE_DIR / 'public'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site / email settings
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')
SHOP_NAME = os.environ.get('SHOP_NAME', 'Jalaram Computers')
SHOP_PHONE = os.environ.get('SHOP_PHONE', '9892848643')
SHOP_EMAIL = os.environ.get('SHOP_EMAIL', 'jalaramcomputers21@gmail.com')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'support@jalaramcomputers.com')

EMAIL_HOST = os.environ.get('SMTP_HOST', '')
EMAIL_PORT = int(os.environ.get('SMTP_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('SMTP_SECURE', 'false').lower() not in ('1', 'true', 'yes')
EMAIL_HOST_USER = os.environ.get('SMTP_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASS', '')
DEFAULT_FROM_EMAIL = os.environ.get('MAIL_FROM', EMAIL_HOST_USER or 'noreply@jalaramcomputers.com')

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

LOGIN_URL = '/account'