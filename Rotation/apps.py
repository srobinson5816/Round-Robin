from django.apps import AppConfig
from django.db.backends.signals import connection_created
from django.conf import settings
import sys

class RotationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Rotation'

    def ready(self):
        from .utils import get_database_location
        from django.db import connections

        if 'test' in sys.argv or 'test_coverage' in sys.argv:
            return

        def update_db_connection(sender, connection, **kwargs):
            connection.settings_dict['NAME'] = str(settings.BASE_DIR / get_database_location())

        connection_created.connect(update_db_connection)
