"""
Django settings for catalog project.
Generated by 'django-admin startproject' using Django 2.1.
For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/
For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

# import dj_database_url
# from decouple import Csv, config
from unipath import Path
import os

# import json
# from six.moves.urllib import request
# from cryptography.x509 import load_pem_x509_certificate
# from cryptography.hazmat.backends import default_backend
from django.utils.translation import ugettext_lazy as _l

# SECURITY WARNING: keep the secret key used in production secret!

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROJECT_DIR = Path(__file__).parent


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'rest_framework',
    'rest_framework_jwt',
    'corsheaders',
    'hvad',
    'health_check',
    'health_check.db',
    # 'health_check.cache',
    'health_check.storage',
    'stream_django',
    'storages',
    'sorl.thumbnail',
    'taggit',
    'taggit_serializer',
    'django_elasticsearch_dsl',
    'django_ses',
    'smuggler',
    'catalog.general',
    'catalog.user_profile',
    'catalog.utils',
    'catalog.file',
    'catalog.post',
    'catalog.category',
    'catalog.product',
    'catalog.company',
    'catalog.community',
    'catalog.employment',
    'catalog.getstream',
    'catalog.supply_request',
    'catalog.messaging',
    'catalog.attribute',
    'catalog.mention',
    'catalog.hashtag',
    'catalog.payments'

]

SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'django_cognito_jwt.JSONWebTokenAuthentication',
    )
    # ,
    # 'DEFAULT_FILTER_BACKENDS': (
    #     'django_filters.rest_framework.DjangoFilterBackend',)
}

ROOT_URLCONF = 'catalog.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'catalog.wsgi.application'

AWS_S3_OBJECT_PARAMETERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'CacheControl': 'max-age=94608000'
}

AWS_STORAGE_BUCKET_NAME = 'uacat-static'
AWS_S3_REGION_NAME = 'eu-central-1'  # e.g. us-east-2


# Tell django-storages the domain to use to refer to static files.
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

# Tell the staticfiles app to use S3Boto3 storage when writing the collected static files (when
# you run `collectstatic`).
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_DEFAULT_ACL = None

EMAIL_BACKEND = 'django_ses.SESBackend'
# Additionally, if you are not using the default AWS region of us-east-1,
# you need to specify a region, like so:
AWS_SES_REGION_NAME = 'eu-west-1'
AWS_SES_REGION_ENDPOINT = 'email.eu-west-1.amazonaws.com'

COGNITO_AWS_REGION = 'eu-central-1'  # 'eu-central-1'
COGNITO_USER_MODEL = 'user_profile.UserProfile'

STATICFILES_LOCATION = 'static'
STATICFILES_STORAGE = 'custom_storages.StaticStorage'
MEDIAFILES_LOCATION = 'media'
DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'


# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = "en"

LANGUAGES = (
    ('uk', _l(u'Ukrainian')),
    ('ru', _l(u'Russian')),
    ('en', _l(u'English')),
)



TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


STATIC_ROOT = os.path.join(BASE_DIR, "../../..", "www", "static")
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, '../../static')
]

MEDIA_ROOT = PROJECT_DIR.parent.child('media')
MEDIA_URL = '/media/'

SUPPORT_EMAIL = 'info@uafine.com'


THUMBNAIL_FORCE_OVERWRITE = True

TAGGIT_CASE_INSENSITIVE = True

NOTIFICATION_SERIALIZER_CLASS = 'notification_object_serializer_class'
ACTIVITY_SERIALIZER_CLASS = 'activity_object_serializer_class'

CITIES_LIGHT_TRANSLATION_LANGUAGES = ['uk', 'ru']
CITIES_LIGHT_INCLUDE_CITY_TYPES = ['PPL', 'PPLA', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLC', 'PPLF', 'PPLG', 'PPLL', 'PPLR',
                                   'PPLS', 'STLMT', ]

SMUGGLER_FORMAT = 'json'
SMUGGLER_FIXTURE_DIR = 'fixtures'
SMUGGLER_EXCLUDE_LIST = ['auth.permission', 'contenttypes']

DEFAULT_PRICE_UAH = 10
DEFAULT_PRICE_USD = 1