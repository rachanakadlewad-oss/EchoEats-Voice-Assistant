import os
import sys
from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        # Run DB initialization when starting server or on Render
        if (
            'runserver' in sys.argv
            or 'gunicorn' in sys.argv[0]
            or any('gunicorn' in arg for arg in sys.argv)
            or os.environ.get('RENDER')
            or os.environ.get('RENDER_INSTANCE_ID')
        ):
            try:
                from setup_db import initialize_database
                initialize_database()
            except Exception as e:
                print(f"[EchoEats] Startup DB setup note: {e}")
