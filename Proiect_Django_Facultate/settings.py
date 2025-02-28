import os
from django.contrib.messages import constants as message_constants
from pathlib import Path


MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-n(5llm&gxez81s=vjzwlyr)ycqvcv93w_n82(xq)1um9*-%@%l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',         # Administration interface
    'django.contrib.auth',          # Authentication and permissions management
    'django.contrib.contenttypes',  # Content types (supports generic models)
    'django.contrib.sessions',      # User session management
    'django.contrib.messages',      # One-time messages for users
    'django.contrib.staticfiles',   # Static file management (CSS, JS, etc.)
   
    # Aplicatii personalizate
    'Brutarie.apps.BrutarieConfig',
    'django.contrib.sitemaps',
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

ROOT_URLCONF = 'Proiect_Django_Facultate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  
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

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'error',
}



WSGI_APPLICATION = 'Proiect_Django_Facultate.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Bucharest'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'brutarie', # Database name
        'USER': 'musat_stefan',  # Username
        'PASSWORD': 'Radoi2004!',  # User password
        'HOST': 'localhost',  # The host on which PostgreSQL is running
        'PORT': '5432',  # PostgreSQL port (default is 5432)
        'OPTIONS': {
            'options': '-c search_path=public'  # Set search_path to django schema
        },
    }
}

STATIC_URL = '/static/'


STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / 'staticfiles' 


AUTH_USER_MODEL = 'Brutarie.CustomUser'

SESSION_COOKIE_AGE = 86400  
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587 
EMAIL_USE_TLS = True 
EMAIL_HOST_USER = 'musatstefan2004@gmail.com'
EMAIL_HOST_PASSWORD = 'biav qbcb utme iznu'
DEFAULT_FROM_EMAIL = 'musatstefan2004@gmail.com'

# CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']
# CSRF_COOKIE_SECURE = False
# CSRF_FAILURE_VIEW = 'Brutarie.views.custom_403_view'

CSRF_FAILURE_VIEW = 'Brutarie.views.csrf_failure' 