from django.apps import AppConfig


class DataModelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'data_models'

    def ready(self):
        # Make sure that signals and tasks are loaded
        import data_models.signals
        import data_models.tasks
