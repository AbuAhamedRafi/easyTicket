"""
Celery configuration for EasyTicket
"""

import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "easyTicket.settings")

app = Celery("easyTicket")

# Load task modules from all registered Django app configs
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery setup"""
    print(f"Request: {self.request!r}")
