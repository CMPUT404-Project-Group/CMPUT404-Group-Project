from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        from app import updater
        updater.update_cached_posts()
        updater.update_cached_authors()
        updater.start()
