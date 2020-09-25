"""
Django settings for bernese project.

"""

import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG',False)

if os.name == 'nt':
    LINUX_SERVER = False
else:
    LINUX_SERVER = True

DOWNLOAD_EPHEM = True

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
if 'DJANGO_KEY' in os.environ:
    SECRET_KEY = os.environ['DJANGO_KEY']
else:
    SECRET_KEY = os.environ['DJANGO_KEY1'] + '#' + os.environ['DJANGO_KEY2']

HOST = os.getenv('HOST','host.docker.internal')
ALLOWED_HOSTS = ['localhost','gnss.ufv.br',HOST]

DATAPOOL_DIR = os.path.join(BASE_DIR,'DATAPOOL')
SAVEDISK_DIR = os.path.join(BASE_DIR,'SAVEDISK')
CAMPAIGN_DIR = os.path.join(BASE_DIR,'CAMPAIGN52','SYSTEM')
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
    'bernese.rede',
    'django_celery_results',
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
DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB','public'),
        'USER': os.getenv('POSTGRES_USER','postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD','123456'),
        'HOST': os.getenv('POSTGRES_HOST','localhost'),
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
if DEBUG: EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
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
MAX_PROCESSING_TIME = 30

# AUTH
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = 'accounts:logout'
AUTH_USER_MODEL = 'accounts.MyUser'

# CELERY
RABBITMQ_DEFAULT_USER = os.getenv('RABBITMQ_DEFAULT_USER','guest')
RABBITMQ_DEFAULT_PASS = os.getenv('RABBITMQ_DEFAULT_PASS','guest')
RABBITMQ_DEFAULT_VHOST = os.getenv('RABBITMQ_DEFAULT_VHOST','')
CELERY_BROKER_URL = 'amqp://{}:{}@rabbitmq:5672/{}'.format(
    RABBITMQ_DEFAULT_USER, RABBITMQ_DEFAULT_PASS, RABBITMQ_DEFAULT_VHOST )
CELERY_RESULT_BACKEND = 'django-db'