# /home/nasirk4/FBR_SEP_Taxpayer_Survey/fbr_survey/settings.py
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Ensure log directory exists
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'fbr_survey.log'
os.makedirs(LOG_DIR, exist_ok=True)
if not LOG_FILE.exists():
    LOG_FILE.touch()

# Security settings
def get_env_variable(var_name, default=None):
    """Get environment variable or return default (if provided)"""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        raise ImproperlyConfigured(f"Set the {var_name} environment variable")

SECRET_KEY = get_env_variable('DJANGO_SECRET_KEY')
DEBUG = get_env_variable('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = get_env_variable('DJANGO_ALLOWED_HOSTS', 'nasirk4.pythonanywhere.com,localhost,127.0.0.1').split(',')

# Explicitly define CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'https://localhost:8000',
    'http://cautious-eureka-jjq99jx6655hqj9j-8000.app.github.dev',
    'https://cautious-eureka-jjq99jx6655hqj9j-8000.app.github.dev',
    'https://*.github.dev',
    'https://nasirk4.pythonanywhere.com',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'survey.apps.SurveyConfig',
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

ROOT_URLCONF = 'fbr_survey.urls'

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

WSGI_APPLICATION = 'fbr_survey.wsgi.application'

# Database - Using SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_SECURE = not DEBUG
SESSION_EXPIRE_AT_BROWSER_CLOSE = not DEBUG

# CSRF settings
CSRF_COOKIE_SECURE = not DEBUG

# Security settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'survey': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'