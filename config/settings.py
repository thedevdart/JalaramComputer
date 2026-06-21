import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def _csv_env(name, default=''):
    return [x.strip() for x in os.environ.get(name, default).split(',') if x.strip()]


def _host_from_url(url):
    if not url:
        return None
    from urllib.parse import urlparse
    return urlparse(url.strip()).hostname


def _expand_host_aliases(hosts):
    """If www.example.com is allowed, also allow example.com (and vice versa)."""
    expanded = list(hosts)
    for host in hosts:
        if host.startswith('.') or host in ('localhost', '127.0.0.1', 'testserver'):
            continue
        if host.startswith('www.'):
            apex = host[4:]
            if apex and apex not in expanded:
                expanded.append(apex)
        elif '.' in host:
            www = f'www.{host}'
            if www not in expanded:
                expanded.append(www)
    return expanded


SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-only-change-in-production')
DEBUG = os.environ.get('DEBUG', 'true').lower() in ('1', 'true', 'yes')

RAILWAY_PUBLIC_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '').strip()
ALLOWED_HOSTS = _csv_env('ALLOWED_HOSTS', 'localhost,127.0.0.1')
_site_host = _host_from_url(os.environ.get('SITE_URL', ''))
if _site_host:
    ALLOWED_HOSTS.append(_site_host)
if RAILWAY_PUBLIC_DOMAIN:
    ALLOWED_HOSTS.append(RAILWAY_PUBLIC_DOMAIN)
if os.environ.get('RAILWAY_ENVIRONMENT'):
    ALLOWED_HOSTS.append('.railway.app')
ALLOWED_HOSTS = list(dict.fromkeys(_expand_host_aliases(ALLOWED_HOSTS)))

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
    'whitenoise.middleware.WhiteNoiseMiddleware',
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

# PostgreSQL via DATABASE_URL (Railway injects this when Postgres is linked)
DATABASE_URL = os.environ.get('DATABASE_URL', '')
_on_railway = bool(os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PUBLIC_DOMAIN'))
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif os.environ.get('USE_SQLITE', '').lower() in ('1', 'true', 'yes'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
elif _on_railway:
    from django.core.exceptions import ImproperlyConfigured
    raise ImproperlyConfigured(
        'DATABASE_URL is required on Railway. Add a PostgreSQL database and link DATABASE_URL to this service.'
    )
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

# WhiteNoise serves collected static files in production (DEBUG=False).
# Compressed (not manifest) storage so the hard-coded /assets/ URLs keep working.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage'},
}
WHITENOISE_MAX_AGE = 31536000

# Serve public/data and other public root files
PUBLIC_DIR = BASE_DIR / 'public'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Site / email settings
SITE_URL = os.environ.get('SITE_URL') or (
    f'https://{RAILWAY_PUBLIC_DOMAIN}' if RAILWAY_PUBLIC_DOMAIN else 'http://localhost:8000'
)

_csrf_origins = _csv_env('CSRF_TRUSTED_ORIGINS')
if RAILWAY_PUBLIC_DOMAIN:
    _csrf_origins.append(f'https://{RAILWAY_PUBLIC_DOMAIN}')
for host in ALLOWED_HOSTS:
    if host.startswith('.') or host in ('localhost', '127.0.0.1', 'testserver'):
        continue
    _csrf_origins.append(f'https://{host}')
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(_csrf_origins))
SHOP_NAME = os.environ.get('SHOP_NAME', 'Jalaram Computers')
SHOP_PHONE = os.environ.get('SHOP_PHONE', '9892848643')
SHOP_EMAIL = os.environ.get('SHOP_EMAIL', 'jalaramcomputers21@gmail.com')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'support@jalaramcomputers.com')

# Google Sign-In (storefront account page). Client ID only — no secret needed for ID-token flow.
GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '').strip()

EMAIL_HOST = os.environ.get('SMTP_HOST', '')
EMAIL_PORT = int(os.environ.get('SMTP_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('SMTP_SECURE', 'false').lower() not in ('1', 'true', 'yes')
EMAIL_HOST_USER = os.environ.get('SMTP_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('SMTP_PASS', '')
DEFAULT_FROM_EMAIL = os.environ.get('MAIL_FROM', EMAIL_HOST_USER or 'noreply@jalaramcomputers.com')

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

LOGIN_URL = '/account'

# ── Production hardening (applied only when DEBUG is off) ──
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'true').lower() in ('1', 'true', 'yes')
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True