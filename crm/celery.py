# crm/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")

app = Celery("crm")

# Load settings from Django config using CELERY_ prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks from all installed apps
app.autodiscover_tasks()
