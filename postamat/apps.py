from django.apps import AppConfig
from dotenv import load_dotenv


class PostamatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'postamat'

    def ready(self):
        import postamat.signals
