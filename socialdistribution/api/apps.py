from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        from app import updater
        updater.start()
        updater.update_cached_posts()
        updater.update_cached_authors()

