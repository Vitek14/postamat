from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.db import connection
import os
from dotenv import load_dotenv

load_dotenv()


class PostamatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'postamat'

    def ready(self):
        call_command('migrate', interactive=False)
        if 'auth_user' in connection.introspection.table_names():
            self._create_superuser()
        else:
            post_migrate.connect(self._create_superuser_on_migrate, sender=self)

    def _create_superuser(self):
        from django.contrib.auth.models import User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(os.environ["SUPERUSER_NICKNAME"],
                                          os.environ["SUPERUSER_EMAIL"],
                                          os.environ["SUPERUSER_PASSWORD"])

    def _create_superuser_on_migrate(self, sender, **kwargs):
        self._create_superuser()
