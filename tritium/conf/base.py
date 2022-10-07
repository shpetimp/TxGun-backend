# -*- coding: utf-8 -*-

from .defaults import *
from datetime import timedelta
from celery.schedules import crontab
import environ

env = environ.Env(DEBUG=(bool, False),) # set default values and casting
DEBUG=os.environ.get('DEBUG', '') == 'true'


INSTALLED_APPS = [
    'django.contrib.auth',
    'jet.dashboard',
    'jet',
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'storages',

    'django_s3_storage',
    'rest_framework',
    'rest_registration',
    'auditlog',

    'django_filters',
    'django_extensions',
    'django_celery_results',

    'tritium.apps.networks',
    'tritium.apps.subscriptions',
    'tritium.apps.errors',
    'tritium.apps.contracts',
    'tritium.apps.users'

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = 'tritium.conf.urls'

REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
    'REGISTER_VERIFICATION_URL': 'https://txgun.io/verify-user/',
    'RESET_PASSWORD_VERIFICATION_URL': 'https://txgun.io/reset-password/',
    'REGISTER_EMAIL_VERIFICATION_URL': 'https://txgun.io/verify-email/',
    'REGISTER_SERIALIZER_CLASS': 'tritium.apps.users.serializers.RegisterUserSerializer',
    'VERIFICATION_FROM_EMAIL': 'noreply@txgun.io',
    'USER_EDITABLE_FIELDS': ['email', 'username', 'first_name', 'last_name', 'default_notify_url', 'no_balance_emails'],
    
}

AUTH_USER_MODEL = 'users.CustomUser'

DATABASES = {
    'default': env.db('DATABASE_URL', default='psql://tritium:tritium@psql/tritium'),
}

LOGGING['loggers']['scanner'] = {
    'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO')
}

LOGGING['loggers']['subscriptions'] = {
    'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO')
}

TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(SITE_ROOT + '/templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            # 'loaders': [
            #     'django.template.loaders.filesystem.Loader',
            #     'django.template.loaders.app_directories.Loader',
            # ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

ALLOWED_HOSTS = ['txgun.io', '127.0.0.1', 'localhost', '*']

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'tritium.apps.users.authentication.APIKeyAuthentication',)
}

if DEBUG:
    BASE_URL="https://api.txgun.io"

    EMAIL_BACKEND = 'django_ses.SESBackend'

    # Additionally, if you are not using the default AWS region of us-east-1,
    # you need to specify a region, like so:
    AWS_SES_REGION_NAME = 'us-east-1'
    AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    BASE_URL="http://localhost:8000"


SIGNUP_BONUS_CREDITS = 2500
MONTHLY_BONUS_CREDITS = 2500
NOTIFICATION_CREDIT_COST = 1
PRICING_DATA_CREDIT_COST = 2
SPECIFIC_CALLS_CREDIT_COST = 1
DAILY_SUMMARY_CREDIT_COST = 5
WEEKLY_SUMMARY_CREDIT_COST = 30
MONTHLY_SUMMARY_CREDIT_COST = 100
TOKEN_TRANSFERS_CREDIT_COST = 1

APPEND_SLASH=True


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

from .eth import *

# REDIS
REDIS_URL = "redis://{host}:{port}/1".format(
    host=os.getenv('REDIS_HOST', 'redis-cluster-master'),
    port=os.getenv('REDIS_PORT', '6379')
)

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        },
        "KEY_PREFIX": "tritium"
    }
}

# CELERY
BROKER_URL = REDIS_URL
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = 'django-cache'
CELERY_BEAT_SCHEDULE = {
}

if os.getenv('NAMESPACE', '') != 'tritium-staging':
    CELERY_BEAT_SCHEDULE['main-scanner'] = {
        'task': 'tritium.celery_app.main_scanner',
        'schedule': crontab(minute='*')
    }

    CELERY_BEAT_SCHEDULE['midnight-job'] = {
        'task': 'tritium.celery_app.midnight_job',
        'schedule': crontab(minute='*', hour='0')
    }

    CELERY_BEAT_SCHEDULE['monthly_summary'] = {
        'task': 'tritium.celery_app.monthly_summary',
        'schedule': crontab(minute='*', hour='0', day_of_month='1')
    }

    CELERY_BEAT_SCHEDULE['daily_summary'] = {
        'task': 'tritium.celery_app.daily_summary',
        'schedule': crontab(minute='*', hour='0')
    }
