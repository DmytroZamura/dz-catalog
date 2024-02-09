from catalog.settings.common import *
import dj_database_url
from decouple import Csv, config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1:8000',
                 'uacat.eu-central-1.elasticbeanstalk.com',
                'localhost:4200', 'localhost:8080',
                 'https://zibuw3rgp6.execute-api.eu-central-1.amazonaws.com',
                 'https://zibuw3rgp6.execute-api.eu-central-1.amazonaws.com/production/'
                 ]

FRONTEND_URL = 'http://localhost:4200/'
LOGO_URL = 'https://uacat-static.s3.eu-central-1.amazonaws.com/media/img/uafine-logo-square-colored.svg'

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL')
    )
}

# CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'localhost:4200',
    'localhost:8080',
    '127.0.0.1:8000',
    'uacat.eu-central-1.elasticbeanstalk.com',
    'https://zibuw3rgp6.execute-api.eu-central-1.amazonaws.com',
    'https://zibuw3rgp6.execute-api.eu-central-1.amazonaws.com/production/',
)

STREAM_LOCATION = 'us-east'

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}

UAFINE_ID = '23'
UAFINE_USER_ID = '30'
ARTICLES_TYPE_ID = 9

EN_LANG_ID = 9

THUMBNAIL_UPSCALE = False
PAYMENT_CALLBACK_URL = 'http://127.0.0.1:8000/api/payment-callback/'