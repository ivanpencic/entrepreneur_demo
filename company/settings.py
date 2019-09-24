from company.base_settings import *
import company

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 't0d4(30lmx^uk1*oitlr^jq0@%op()%!v^gjiwc4gn-@p$(1(p'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = False
DEBUG = True

VER = company.__version__

APP_LANGAUGE_ID = 1

ALLOWED_HOSTS = ['*']

LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'handlers': {
		'console': {
			'class': 'logging.StreamHandler',
		},
		'applogfile': {
			'class': 'logging.handlers.RotatingFileHandler',
			'filename': os.path.join(BASE_DIR, 'logs.log'),
			'maxBytes': 1024 * 1024 * 10,
		},
	},
	'loggers': {
		'django': {
			'handlers': ['console', 'applogfile'],
			'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
		},
	},
}


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(BASE_DIR, 'demo.db'),
	}
}

# SMTP mail server
DEFAULT_MAIL_SERVER = 'smtp.gmail.com'
DEFAULT_MAIL_SERVER_PORT = 465

# wkhtml binary
WKHTML_BIN_PATH = '/app/bin/wkhtmltopdf'
# WKHTML_BIN_PATH = '/usr/bin/wkhtmltopdf'
