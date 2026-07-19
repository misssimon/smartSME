"""
Django settings for smartSME project - LOCAL DEVELOPMENT CONFIG
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-#)xw42($8*e*egi!)ecw&kck!pr8odfj@czmnligr#fka60+vq'
DEBUG = True

ALLOWED_HOSTS = ['*']   # Safe for local development

# =============================================================================
# ALLAUTH CONFIGURATION (Important!)
# =============================================================================

# Disable allauth's default account pages so your custom views take priority
ACCOUNT_LOGIN_ON_PASSWORD_RESET = False
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'
ACCOUNT_LOGIN_REDIRECT_URL = '/'   # or 'dashboard:home' later

# Tell allauth to use your custom login/signup URLs
LOGIN_REDIRECT_URL = '/'                    # After successful login
LOGOUT_REDIRECT_URL = '/accounts/login/'    # After logout

# Optional: Make allauth not override your templates completely
ACCOUNT_TEMPLATE_REDIRECT = None

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_otp',
    'django_otp_webauthn',

    # Custom apps
    'accounts',
    'dashboard',
    'checkout',
    'payment',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'smartSME.urls'

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

WSGI_APPLICATION = 'smartSME.wsgi.application'

# =============================================================================
# DATABASE - LOCAL SQLITE (Development)
# =============================================================================
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}

# Production database (commented out)
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///db.sqlite3')
}

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC & MEDIA
# =============================================================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# EMAIL - LOCAL DEVELOPMENT
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'   # Prints emails in terminal

# Production Email (Gmail) - Commented Out
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'soshisunny073@gmail.com'
EMAIL_HOST_PASSWORD = 'smqictmqccptacqe'
DEFAULT_FROM_EMAIL = 'smartSME <noreply@smartSME.local>'

# =============================================================================
# AUTHENTICATION
# =============================================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# =============================================================================
# WEBAUTHN / BIOMETRIC SETTINGS
# =============================================================================
OTP_WEBAUTHN_RP_ID = 'localhost'
OTP_WEBAUTHN_RP_NAME = 'smartSME'

OTP_WEBAUTHN_ALLOWED_ORIGINS = [
    'https://smartsme.onrender.com',
    'https://127.0.0.1:8000',
]

# Allow HTTP for local development (important!)
OTP_WEBAUTHN_ALLOW_HTTP = False