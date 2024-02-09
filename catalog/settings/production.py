from catalog.settings.common import *
from django.core.exceptions import ImproperlyConfigured

import requests

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

FRONTEND_URL = 'https://www.uafine.com/'
LOGO_URL = 'https://uacat-static.s3.eu-central-1.amazonaws.com/media/img/uafine-logo-square-colored.svg'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['RDS_DB_NAME'],
        'USER': os.environ['RDS_USERNAME'],
        'PASSWORD': os.environ['RDS_PASSWORD'],
        'HOST': os.environ['RDS_HOSTNAME'],
        'PORT': os.environ['RDS_PORT'],
    }
}

CORS_ORIGIN_WHITELIST = (
    'www.uafine.com',
    'api.uafine.com',
)

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

CORS_URLS_REGEX = r'^/api/.*$'

CORS_ORIGIN_REGEX_WHITELIST = [
    r"^https://\w+\.uafine\.com$",
]


def get_ec2_hostname():
    try:
        ipconfig = 'http://169.254.169.254/latest/meta-data/local-ipv4'
        return requests.get(ipconfig, timeout=10).text
    except Exception:
        error = 'You have to be running on AWS to use AWS settings'
        raise ImproperlyConfigured(error)


ALLOWED_HOSTS = [
    get_ec2_hostname(),
    'www.uafine.com',
    'api.uafine.com',
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STREAM_LOCATION = 'us-east'

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'https://vpc-catalog-test-yyr3kyzipr4mzgbt6z24wgfm24.eu-central-1.es.amazonaws.com'

    },
}

UAFINE_ID = '23'
UAFINE_USER_ID = '30'
ARTICLES_TYPE_ID = 7
EN_LANG_ID = 9

CACHES = {
    'default': {
        'BACKEND': 'django_elastipymemcache.memcached.ElastiPyMemCache',
        'LOCATION': 'uafine-cashe-micro.jdfbfx.cfg.euc1.cache.amazonaws.com:11211',
        'OPTIONS': {
            'cluster_timeout': 1,  # its used when get cluster info
            'ignore_exc': True,  # pymemcache Client params
            'ignore_cluster_errors': True,  # ignore get cluster info error
        }
    }
}

THUMBNAIL_UPSCALE = False