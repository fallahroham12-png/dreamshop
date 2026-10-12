"""
تنظیمات اصلی پروژه فروشگاه نیکا (Nika Store)
مستندات هر بخش به‌صورت کامنت فارسی آمده تا نگهداری پروژه ساده باشد.
"""

from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================
# امنیت پایه
# ==============================================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-CHANGE-ME-IN-PRODUCTION')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ==============================================================
# اپلیکیشن‌ها
# ==============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # پکیج‌های شخص ثالث
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'corsheaders',

    # اپ‌های پروژه
    'core',
    'accounts',
    'catalog',
    'orders',
    'payments',
    'promotions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================
# دیتابیس
# در Production از PostgreSQL و در توسعه (در صورت نبود متغیرهای DB) از SQLite استفاده می‌شود.
# ==============================================================
if config('DB_NAME', default=''):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==============================================================
# کاربر سفارشی (ورود با شماره موبایل)
# ==============================================================
AUTH_USER_MODEL = 'accounts.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================
# بین‌المللی‌سازی — فارسی / ایران
# ==============================================================
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

# ==============================================================
# فایل‌های استاتیک و مدیا (تصاویر محصولات)
# ==============================================================
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
}

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================
# Django REST Framework
# ==============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '120/minute',
        'user': '300/minute',
    },
}

# ==============================================================
# CORS — اجازه دسترسی فرانت‌اند به API
# ==============================================================
CORS_ALLOWED_ORIGINS = config('FRONTEND_ORIGIN', default='http://localhost:3000', cast=Csv())
CORS_ALLOW_CREDENTIALS = True

# در حالت توسعه (DEBUG=True)، فرانت‌اند معمولاً از یک فایل محلی (file://) یا پورت متغیر
# اجرا می‌شود، بنابراین محدودیت CORS موقتاً برداشته می‌شود تا اتصال محلی راحت باشد.
# در Production (DEBUG=False) این خط اجرا نمی‌شود و فقط CORS_ALLOWED_ORIGINS بالا معتبر است.
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

# ==============================================================
# امنیت تکمیلی — طبق سند نیازمندی (بخش ۲۲: امنیت)
# ==============================================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

CSRF_TRUSTED_ORIGINS = config('FRONTEND_ORIGIN', default='http://localhost:3000', cast=Csv())

# ==============================================================
# درگاه پرداخت زرین‌پال
# ==============================================================
ZARINPAL_MERCHANT_ID = config('ZARINPAL_MERCHANT_ID', default='')
ZARINPAL_SANDBOX = config('ZARINPAL_SANDBOX', default=True, cast=bool)
ZARINPAL_CALLBACK_URL = config('ZARINPAL_CALLBACK_URL', default='http://localhost:8000/api/payments/verify/')

# ==============================================================
# تنظیمات فروشگاه (قابل استفاده در templates / admin header)
# ==============================================================
STORE_NAME = 'نیکا'
STORE_DEFAULT_SHIPPING_COST = 70000  # تومان — می‌تواند بعداً به یک مدل تنظیمات پویا منتقل شود

ADMIN_SITE_HEADER = 'پنل مدیریت فروشگاه نیکا'
ADMIN_SITE_TITLE = 'نیکا'
ADMIN_INDEX_TITLE = 'مدیریت فروشگاه'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
