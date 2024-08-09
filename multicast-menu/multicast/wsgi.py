import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "multicast.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "multicast.settings"

application = get_wsgi_application()
