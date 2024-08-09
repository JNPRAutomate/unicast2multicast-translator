from __future__ import absolute_import
import celery.schedules
from pathlib import Path
import mimetypes
import dj_database_url
import os
from importlib_metadata import entry_points
from .s3_settings import *

from ..celery import app as celery_app

# Associate .m3u8 file extension with the MIME type "application/vnd.apple.mpegurl"
mimetypes.add_type("application/vnd.apple.mpegurl", ".m3u8")

# secret key
SECRET_KEY = "BGpQn4zCYDQlJNxO3790oZkf9AzimUeISww7OvmGSDH7tyjwEIZIs0xTrx3q_TtOil4"

# Basic Settings
BASE_DIR = Path(__file__).resolve().parent.parent

# Applications
INSTALLED_APPS = [
    "multicast.apps.add",
    "multicast.apps.manage",
    "multicast.apps.view",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "storages",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "multicast.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "multicast.wsgi.application"

# Database
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    "default": dj_database_url.parse(
        "postgresql://multicast-db_owner:g2YlDnE6oKtb@ep-tight-math-a580rdl2.us-east-2.aws.neon.tech/multicast-db?sslmode=require"
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Login settings
LOGIN_URL = "/login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
STATIC_ROOT = BASE_DIR / "serve"

# S3 settings
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
MEDIA_ROOT = BASE_DIR / "media"

# Ensure the media directory exists
os.makedirs(MEDIA_ROOT, exist_ok=True)

DEBUG = True

# Defaults
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Celery settings
CELERY_BROKER_URL = "redis://:p3ad4a1263cb47a3fa6a15a40c45eb98677bbca3552fee9391e3763b7606b9441@ec2-44-221-228-247.compute-1.amazonaws.com:17389"
CELERY_RESULT_BACKEND = "redis://:p3ad4a1263cb47a3fa6a15a40c45eb98677bbca3552fee9391e3763b7606b9441@ec2-44-221-228-247.compute-1.amazonaws.com:17389"
# CELERY_BROKER_URL = "redis://localhost:6379"
# CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_BEAT_SCHEDULE = {
    "scrape_for_streams": {
        "task": "multicast.apps.add.tasks.scrape_for_streams",
        "schedule": celery.schedules.crontab(minute=0, hour=0),
        "args": (),
    },
    "clean_inactive_streams": {
        "task": "multicast.apps.add.tasks.clean_inactive_streams",
        "schedule": celery.schedules.crontab(minute=0, hour=1),
        "args": (),
    },
}

# CORS Header
CORS_ALLOW_ALL_ORIGINS = True

# Allow every host and custom domain
ALLOWED_HOSTS = ["*", "www.treedn.net"]

# Trending streams constants
TRENDING_STREAM_USAGE_WEIGHT = 0.9
TRENDING_STREAM_INIT_SCORE = 1.0
TRENDING_STREAM_MAX_SIZE = 20
TRENDING_STREAM_MAX_VISIBLE_SIZE = 10

# Check for Heroku environment
if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config()}

# Import secret.py
try:
    from .secret import *
except ImportError:
    pass

# Import S3 settings
# from .s3_settings import *