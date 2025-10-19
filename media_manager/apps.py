from django.apps import AppConfig


class MediaManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media_manager'
    verbose_name = 'Media Manager'

    def ready(self):
        # Import signals to ensure post_migrate seeder runs after migrations
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid raising during manage.py commands where imports may fail
            pass
