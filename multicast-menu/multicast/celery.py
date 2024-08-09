import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multicast.settings")

app = Celery("multicast")

# Celery Configuration
app.conf.update(
    broker_pool_limit=10,
    broker_connection_max_retries=None,
    broker_connection_retry=True,
    broker_connection_timeout=30,
    broker_connection_retry_on_startup=True,
    result_backend=os.environ.get("REDIS_URL"),
    redis_max_connections=10,
    broker_pool_recycle=3600,
)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(["multicast.apps.view.tasks"])
