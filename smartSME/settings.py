"""
Django settings for smartSME project.
Updated with proper configuration for development
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# =============================================================================
# SECURITY WARNINGS
# =============================================================================
SECRET_KEY = 'django-insecure-#)xw42($8*e*egi!)ecw&kck!pr8odfj@czmnligr#fka60+vq'

DEBUG = True

# ====================== ALLOWED_HOSTS (FIXED) ======================
if DEBUG:
    ALLOWED_HOSTS = ['*']                    # Best for local development
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
# ===================================================================


# =============================================================================
# APPLICATION DEFINITION
# =============================================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your custom apps
    'accounts',
    'dashboard',
    'checkout',
    'payment',

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

ROOT_URLCONF = 'smartSME.urls'

# ====================== TEMPLATES (UPDATED) ======================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # ← Points to your templates folder
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
# =================================================================

WSGI_APPLICATION = 'smartSME.wsgi.application'


# =============================================================================
# DATABASE
# =============================================================================
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR / 'db.sqlite3',
#    }
#}
#
import dj_database_url
import os

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}

# For Render.com PostgreSQL
if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'])

# =============================================================================
# PASSWORD VALIDATION
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'          # ← Changed to Kenya time
USE_I18N = True
USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# =============================================================================
# MEDIA FILES (For Product Images - Very Important!)
# =============================================================================
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# EMAIL (For welcome emails during development)
# =============================================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'