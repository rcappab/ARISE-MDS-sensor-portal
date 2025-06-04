from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sensor_portal.settings")

app = Celery("sensor_portal")

app.config_from_object(settings, namespace="CELERY")
app.set_default()
app.set_current()
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
