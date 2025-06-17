from django.apps import AppConfig


class DSIConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dsi'

    def ready(self):
        import dsi.tasks
