"""
Django settings for AJERES.
Env-based config ready for DigitalOcean App Platform / Droplet.
"""

import os
import sys
from pathlib import Path

from csp.constants import NONE, NONCE, SELF, UNSAFE_INLINE
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

IS_VERCEL = os.environ.get('VERCEL') == '1'


def _is_management_command(*names: str) -> bool:
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    return bool(args) and args[0] in names


_IS_BUILD_CMD = _is_management_command('collectstatic', 'check')

DEBUG = os.environ.get('DEBUG', 'False').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # collectstatic on Vercel has no runtime secrets; Droplet still requires SECRET_KEY.
    if DEBUG or IS_VERCEL or _IS_BUILD_CMD:
        SECRET_KEY = get_random_secret_key()
    else:
        raise ImproperlyConfigured('SECRET_KEY environment variable is required')

# Non-default admin path (security through obscurity). Override via ADMIN_URL.
_ADMIN_SLUG = (os.environ.get('ADMIN_URL') or 'f7YG0XG1JUr0iUzF').strip().strip('/')
if not _ADMIN_SLUG or _ADMIN_SLUG.lower() == 'admin':
    _ADMIN_SLUG = 'f7YG0XG1JUr0iUzF'
ADMIN_URL = f'{_ADMIN_SLUG}/'
ADMIN_PATH_PREFIX = f'/{_ADMIN_SLUG}'

ALLOWED_HOSTS = [
    h.strip()
    for h in os.environ.get(
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1,testserver,.vercel.app,ajeres.uz,www.ajeres.uz',
    ).split(',')
    if h.strip()
]
if IS_VERCEL:
    for _host in (
        '.vercel.app',
        'ajeres.uz',
        'www.ajeres.uz',
        os.environ.get('VERCEL_URL', '').strip(),
        os.environ.get('VERCEL_PROJECT_PRODUCTION_URL', '').strip(),
    ):
        if _host and _host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_host)

CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if o.strip()
]
if IS_VERCEL:
    _vercel_csrf = [
        'https://*.vercel.app',
        'https://ajeres.uz',
        'https://www.ajeres.uz',
    ]
    _vercel_url = os.environ.get('VERCEL_URL', '').strip()
    _vercel_prod = os.environ.get('VERCEL_PROJECT_PRODUCTION_URL', '').strip()
    if _vercel_url:
        _vercel_csrf.append(f'https://{_vercel_url}')
    if _vercel_prod:
        _vercel_csrf.append(
            _vercel_prod if _vercel_prod.startswith('http') else f'https://{_vercel_prod}'
        )
    CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS + _vercel_csrf))
if not DEBUG and not CSRF_TRUSTED_ORIGINS and not _IS_BUILD_CMD:
    raise ImproperlyConfigured(
        'CSRF_TRUSTED_ORIGINS is required when DEBUG is False'
    )

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'csp',
    'apps.core',
    'apps.catalog',
    'apps.leads',
]


def _admin_navigation(request):
    from apps.core.admin_nav import build_navigation

    return build_navigation(request)


# Plain strings / callables only: Vercel JSON-serializes settings before django.setup().
# Never put reverse_lazy / gettext_lazy values directly in UNFOLD.
UNFOLD = {
    'SITE_TITLE': 'AJERES Admin',
    'SITE_HEADER': 'AJERES',
    'SITE_SYMBOL': 'storefront',
    'SITE_URL': '/',
    'SITE_LOGO': 'apps.core.unfold_theme.site_logo',
    'SITE_FAVICONS': 'apps.core.unfold_theme.site_favicons',
    'BORDER_RADIUS': '10px',
    'COLORS': 'apps.core.unfold_theme.unfold_colors',
    'STYLES': ['apps.core.unfold_theme.admin_styles'],
    'SCRIPTS': ['apps.core.unfold_theme.admin_scripts'],
    'SIDEBAR': {
        'show_search': True,
        'command_search': True,
        'show_all_applications': False,
        'navigation': _admin_navigation,
    },
    'EXTENSIONS': {
        'modeltranslation': {
            'flags': {
                'ru': 'RU',
                'uz': 'UZ',
                'en': 'EN',
            },
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'csp.middleware.CSPMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'apps.core.middleware.PreferDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'apps.core.middleware.AdminForceRussianMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.AdminUploadLimitMiddleware',
]

# CSP: style-src дозволяє 'unsafe-inline' через CSS custom properties у шаблонах
# (home hero-stats --i/--rev) та JS element.style у каруселі. script-src суворий.
CONTENT_SECURITY_POLICY = {
    # ADMIN_URL already has a trailing slash; prefix must match /{slug}/…
    'EXCLUDE_URL_PREFIXES': [f'{ADMIN_PATH_PREFIX}/'],
    'DIRECTIVES': {
        'default-src': [SELF],
        'script-src': [SELF, NONCE],
        'style-src': [SELF, UNSAFE_INLINE, 'https://fonts.googleapis.com'],
        'font-src': [SELF, 'https://fonts.gstatic.com', 'data:'],
        'img-src': [SELF, 'data:', 'blob:'],
        'connect-src': [SELF],
        # Google Maps embed on contacts page.
        'frame-src': [SELF, 'https://www.google.com', 'https://maps.google.com'],
        'frame-ancestors': [NONE],
        'base-uri': [SELF],
        'form-action': [SELF],
    },
}

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
if DATABASE_URL.startswith('postgres'):
    # Managed Postgres (Neon / Vercel / DigitalOcean)
    import urllib.parse as urlparse

    url = urlparse.urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:],
            'USER': url.username,
            'PASSWORD': url.password,
            'HOST': url.hostname,
            'PORT': url.port or 5432,
            'OPTIONS': {'sslmode': os.environ.get('DB_SSLMODE', 'require')},
        }
    }
elif IS_VERCEL:
    # Serverless FS is read-only except /tmp — demo SQLite (ephemeral).
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': Path('/tmp') / 'ajeres.sqlite3',
        }
    }
else:
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

LANGUAGE_CODE = 'ru'

# Plain strings (not gettext_lazy): Vercel imports settings before django.setup().
# Default language first — used when Accept-Language is ignored on first visit.
LANGUAGES = [
    ('ru', 'Русский'),
    ('uz', "O'zbekcha"),
    ('en', 'English'),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = 'ru'
MODELTRANSLATION_LANGUAGES = ('ru', 'uz', 'en')
MODELTRANSLATION_FALLBACK_LANGUAGES = {'default': ('ru', 'en', 'uz')}

TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [BASE_DIR / 'locale']

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STORAGES = {
    'default': {
        'BACKEND': 'apps.core.webp_storage.WebPFileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': (
            'django.contrib.staticfiles.storage.StaticFilesStorage'
            if DEBUG or IS_VERCEL
            else 'whitenoise.storage.CompressedStaticFilesStorage'
        ),
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = (Path('/tmp') / 'ajeres-media') if IS_VERCEL else (BASE_DIR / 'media')
DATA_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024 + 512 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024

# Vercel function has no persistent STATIC_ROOT; serve from STATICFILES_DIRS.
if IS_VERCEL:
    WHITENOISE_USE_FINDERS = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Catalog
CATALOG_PER_PAGE = int(os.environ.get('CATALOG_PER_PAGE', '72'))

PUBLIC_SITE_URL = (os.environ.get('PUBLIC_SITE_URL') or 'https://ajeres.uz').strip()

# Security (production)
# SECURE_SSL_REDIRECT=False у Docker до SSL (інакше healthcheck 301 → unhealthy)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    SECURE_SSL_REDIRECT = os.environ.get(
        'SECURE_SSL_REDIRECT',
        'False' if IS_VERCEL else 'True',
    ).lower() in (
        '1',
        'true',
        'yes',
    )
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    CSRF_COOKIE_SAMESITE = 'Strict'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    X_FRAME_OPTIONS = 'DENY'
