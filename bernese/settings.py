"""
Django settings for bernese project.

"""

import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEST_SERVER = True
LINUX_SERVER = False


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if LINUX_SERVER:
    SECRET_KEY = os.environ['DJANGO_KEY1'] + '#' + os.environ['DJANGO_KEY2']
else:
    SECRET_KEY = os.environ['DJANGO_KEY']


ALLOWED_HOSTS = ['*']

if TEST_SERVER:
    DATAPOOL_DIR = os.path.join(BASE_DIR,'DATAPOOL')
    SAVEDISK_DIR = os.path.join(BASE_DIR,'SAVEDISK')
    CAMPAIGN_DIR = os.path.join(BASE_DIR,'CAMPAIGN52','SYSTEM')
else:
    DATAPOOL_DIR = 'E:\\Sistema\\GPSDATA\\DATAPOOL\\'
    SAVEDISK_DIR = 'E:\\Sistema\\GPSDATA\\SAVEDISK\\'
    CAMPAIGN_DIR = 'E:\\Sistema\\GPSDATA\\CAMPAIGN52\\SYSTEM'

RESULTS_DIR = os.path.join(BASE_DIR,'RESULTADOS')
RINEX_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR,'RINEX_UPLOAD_TEMP_DIR')

MEDIA_ROOT = RINEX_UPLOAD_TEMP_DIR
MEDIA_URL = '/media/'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bernese.core',
    'bernese.ppp',
    'bernese.relativo',
    'bernese.accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
]

ROOT_URLCONF = 'bernese.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'bernese.wsgi.application'


# Database
if TEST_SERVER:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }

elif LINUX_SERVER:
    DATABASES = {
         'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'gnss_ufv',
            'USER': 'sistema',
            'PASSWORD': os.environ['SYSTEM_MAIL_PASS'],
            'HOST': '200.235.135.143',
            'PORT': '5432',
            }
    }

else:
    DATABASES = {
         'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'gnss_ufv',
            'USER': 'sistema',
            'PASSWORD': os.environ['SYSTEM_MAIL_PASS'],
            'HOST': '127.0.0.1',
            'PORT': '5432',
            }
    }


# Password validation

AUTH_PASSWORD_VALIDATORS = [
# {
#     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
# },
# {
#     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
# },
# {
#     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
# },
# {
#     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
# },
]




# Internationalization

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, 'bernese', 'static'))
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'bernese', "static_source"),
]

# E-mail
if TEST_SERVER: EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else: EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'GNSS-UFV <gnss.ufv@gmail.com>'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'gnss.ufv@gmail.com'
EMAIL_HOST_PASSWORD = os.environ['SYSTEM_MAIL_PASS']
EMAIL_PORT = 587
CONTACT_EMAIL = 'gnss.ufv@gmail.com'

ADMINS = [('Gabriel','gabriel.diniz@ufv.br'),('GNSS-UFV', 'gnss.ufv@gmail.com')]
MANAGERS = ADMINS

SERVER_EMAIL = 'gnss.ufv@gmail.com'
SERVER_NAME = 'GNSS-UFV'

# Tempo limite aguardando um processamento. Em minutos.
MAX_PROCESSING_TIME = 10

# AUTH
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = 'accounts:logout'
AUTH_USER_MODEL = 'accounts.MyUser'
