"""
WSGI config for sensor_portal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.db.backends.signals import connection_created
from django.dispatch import receiver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sensor_portal.settings')

application = get_wsgi_application()


@receiver(connection_created)
def setup_postgres(connection, **kwargs):
    if connection.vendor != 'postgresql':
        return

    print("Set statement timeout")

    # Timeout statements after 120 seconds.
    with connection.cursor() as cursor:
        cursor.execute("SET statement_timeout TO 120000;")
