"""
WSGI config for Backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')

application = get_wsgi_application()

try:
    from setup_db import initialize_database
    initialize_database()
except Exception as e:
    print("[EchoEats] WSGI initialize_database warning:", e)
