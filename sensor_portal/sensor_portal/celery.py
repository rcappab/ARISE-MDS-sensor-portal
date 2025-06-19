from __future__ import absolute_import, unicode_literals

import logging
import os

from celery import Celery
from django.conf import settings

logger = logging.getLogger(__name__)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sensor_portal.settings")

app = Celery("sensor_portal")

app.config_from_object(settings, namespace="CELERY")
app.set_default()
app.set_current()
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    logger.info(f"Request: {self.request!r}")
