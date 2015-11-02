"""
Django settings for dataproject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

#for celery use
from __future__ import absolute_import
from datetime import timedelta

#celery settings

CELERY_TASK_RESULT_EXPIRES=3600,
CELERYBEAT_SCHEDULE = {
    'get_travel_time-every-30-seconds': {
        'task': 'traffic.tasks.get_travel_time_tmc',
        'schedule': timedelta(seconds=30),
    },
}

#broker url for celery use
BROKER_URL = 'django://'

#periodical schedules


#Django settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
#import kombu
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# for nginx to server static files
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*d7jnjdq6ng4w_u0$ilw5lyd-s&b9y@kb%!cg=jbx1f7hw^r3q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['mac.heinz.cmu.edu']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'traffic',
    'kombu.transport.django',
    'djcelery',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'project_middleware.authen_middleware.LoginRequiredMiddleware',
)

ROOT_URLCONF = 'dataproject.urls'

WSGI_APPLICATION = 'dataproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dataproject',
	    'USER': 'root',
	    'PASSWORD': 'dataproject',
        #'HOST': '52.1.172.127',
        #'HOST': 'LOCALHOST',
        'HOST': '128.2.84.231',
        'PORT': '3306',

    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# for login use
LOGIN_URL = '/traffic/login/'

LOGIN_EXEMPT_URLS = (
)
