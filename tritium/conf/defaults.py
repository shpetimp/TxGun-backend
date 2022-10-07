# -*- coding: utf-8 -*-

import os, sys

project_dir = os.path.dirname(os.path.abspath(__file__))

here = lambda *x: os.path.join(os.path.abspath(os.path.dirname(__file__)), *x)

SITE_ROOT = PROJECT_ROOT = os.path.abspath(here('..'))
PROJECT_MODULE = SITE_ROOT.split('/')[-1]

root = lambda *x: os.path.join(os.path.abspath(PROJECT_ROOT), *x)

DEBUG = False
DEVELOP = False
SERVE_MEDIA = True
USE_TZ = True

# BELOW IS CONFUSING!
# MEDIA_{ROOT,URL} -> User generated content
MEDIA_ROOT = root('static', 'uploads')
MEDIA_URL = '/static/uploads/'

# STATIC_{ROOT,URL} -> Python-collected static content
STATIC_ROOT = root('static', 'assets')
STATIC_URL = '/static/assets/'

# Where to collect ^above^ from:
STATICFILES_DIRS = (
    root('assets'),
)

# Where the admin stuff lives
ADMIN_MEDIA_PREFIX = '/static/assets/admin/'

# django-mediagenerator search directories
# files are defined in assets.py
GLOBAL_MEDIA_DIRS = [root('media'), ]

ROOT_URLCONF = 'conf.urls'

TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"

INTERNAL_IPS = [
    "127.0.0.1",
    "10.0.2.2"
]
ADMINS = [
    ("admin", "admin@txgun.io"),
]
SERVER_EMAIL = 'noreply@txgun.io'
IS_TEST = False

MANAGERS = ADMINS

SITE_ID = 1

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s |'
                       '%(pathname)s:%(lineno)d (in %(funcName)s) |'
                       ' %(message)s ')
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
            'require_debug_false': {
                        '()': 'django.utils.log.RequireDebugFalse',
                    }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEST_EXCLUDE = ('django',)
FIXTURE_DIRS = [
    root(PROJECT_ROOT, "fixtures"),
]

BASE_DIR = root(PROJECT_ROOT)

MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URLNAME = 'home'

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

AUTHENTICATED_EXEMPT_URLS = [
    r"^/$",
    r"^/admin",
    r"^/compiled-media",
    r"^/waitinglist",
    r"^/__debug__",
]

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

ACCOUNT_OPEN_SIGNUP = False
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auditlog.middleware.AuditlogMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    'http://localhost:8080',
    'https://txgun.io'
)
CORS_ALLOW_CREDENTIALS = True
