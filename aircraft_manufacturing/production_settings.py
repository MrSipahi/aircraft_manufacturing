"""
Django settings for aircraft_manufacturing project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
from datetime import timedelta, datetime

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-)s_qlecv_24fiqz$jm)f79h+_zdn=^^i0e(cz93-_q&t85uo#='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.humanize",
    'debug_toolbar',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_yasg',
    
    

    'accounts.apps.AccountsConfig',
    'core.apps.CoreConfig',
]

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.JWTAuthenticationMiddleware',
]

ROOT_URLCONF = 'aircraft_manufacturing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR / "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'
            ],
        },
    },
]

WSGI_APPLICATION = 'aircraft_manufacturing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'aircraft_manufacturing',
        'USER': 'django_user',
        'PASSWORD': 'django_password',
        'HOST': 'db',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


INTERNAL_IPS = [

    "127.0.0.1",
    "localhost"

]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


# Rest Framework ayarları
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
}

# Swagger Settings
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        }
    },
    'USE_SESSION_AUTH': True,  # Session authentication için
    'OPERATIONS_SORTER': 'alpha',  # Operasyonları alfabetik sırala
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEFAULT_MODEL_RENDERING': 'example',
    'LOGIN_URL': 'login',
    'LOGOUT_URL': 'logout',
}

# Logger Settings
LOGS_DIR = BASE_DIR / 'logs'
All_LOGS = LOGS_DIR / 'all'
ERROR_LOGS = LOGS_DIR / 'error'

# Klasörleri oluştur
All_LOGS.mkdir(parents=True, exist_ok=True)
ERROR_LOGS.mkdir(parents=True, exist_ok=True)

# Günün tarihi
current_date = datetime.now().strftime('%Y-%m-%d')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '[%(asctime)s] %(levelname)s  "%(message)s" - User: "%(user)s", Path: "%(path)s", Detail: "%(detail)s"',
            'datefmt': '%d/%m/%Y %H:%M:%S'
        },
        
        'request_formatter': {
            'format': '[%(asctime)s] %(levelname)s  "%(message)s"',
            'datefmt': '%d/%m/%Y %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'info_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': All_LOGS / f'{current_date}.log',
            'maxBytes': 5 * 1024 * 1024,  
            'backupCount': 5,   
            'formatter': 'standard',
            'level': 'INFO'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ERROR_LOGS / f'{current_date}.log',
            'maxBytes': 10 * 1024 * 1024, 
            'backupCount': 5,  
            'formatter': 'standard',
            'level': 'ERROR'
        },
        'request_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'all' / f'{current_date}.log',
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'request_formatter',
        }
    },
    'loggers': {
        '': {  
            'handlers': ['console', 'info_file', 'error_file'],
            'level': 'INFO',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['request_handler'],
            'level': 'INFO',
            'propagate': False,
        }
    }
}


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'accounts.CustomUser'