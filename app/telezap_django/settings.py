import os, sys
from pathlib import Path
from decouple import config
from django.contrib.messages import constants


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', cast=str)

DEBUG = config('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=str).split(" ")

# To save session for 12 hours
SESSION_COOKIE_AGE = 43200
SESSION_SAVE_EVERY_REQUEST = True

# To paginate messages in chat
MESSAGES_PAGINATION = 10

INSTALLED_APPS = [
    # internal apps
    'apps.user',
    'apps.notification',
    'apps.chat',
    'apps.group_chat',
    'apps.videocall',
    # external apps
    'daphne',
    'rest_framework',
    'django_extensions',
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # debug_toolbar must be the last app
    'debug_toolbar',
]

# To use rest_framework_simplejwt
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'telezap_django.middlewares.DisableCSRFMiddlewareInNgrok.DisableCSRFMiddlewareInNgrok'
]


ROOT_URLCONF = 'telezap_django.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'templates' ],
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


WSGI_APPLICATION = 'telezap_django.wsgi.application'
ASGI_APPLICATION = "telezap_django.asgi.application"


LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL='/'
SIGNUP_REDIRECT_URL='/login'
LOGIN_URL='/login'


AUTH_USER_MODEL='user.User'

# To use console email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


DATABASES = {
    "default": {
        "ENGINE": config('SQL_ENGINE', cast=str, default="django.db.backends.sqlite3"),
        "NAME": config('SQL_DATABASE', cast=str, default=BASE_DIR / "db.sqlite3"),
        "USER": config('SQL_USER', cast=str, default="user"),
        "PASSWORD": config('SQL_PASSWORD', cast=str, default="password"),
        "HOST": config('SQL_HOST', cast=str, default="localhost"),
        "PORT": config('SQL_PORT', cast=str, default="5432"),
    },
}


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


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'templates', 'static')
]


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
MEDIAFILES_DIRS = [
    os.path.join(BASE_DIR, 'mediafiles')
]


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# To use django.contrib.messages
MESSAGE_TAGS = {
    constants.DEBUG: 'alert-primary',
    constants.ERROR: 'alert-danger',
    constants.WARNING: 'alert-warning',
    constants.SUCCESS: 'alert-success',
    constants.INFO: 'alert-info ',
}


if DEBUG:
    # To use channels locally
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
    # To use debug_toolbar
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]
    INTERNAL_IPS = [ 
        "127.0.0.1",
    ]
    if 'test' in sys.argv: # To run tests without debug_toolbar
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: False
        }
    else:
        DEBUG_TOOLBAR_CONFIG = {
            'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
        }
else:
    # To use channels in production
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("localhost", 6379)],
            },
        },
    }