from django.apps import AppConfig


class MediaManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media_manager'
    
    def ready(self):
        # Import signal handlers to ensure post_migrate seeder runs when appropriate
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid crashing app import if signals fail to import in some environments
            pass
    verbose_name = 'Media Manager'

    def ready(self):
        # Import signal handlers to register post_migrate seeder
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid breaking startup if signals import fails; errors will be logged
            import logging
            logging.getLogger(__name__).exception('Failed to import media_manager signals')
    verbose_name = 'Media Manager'

    def ready(self):
        # Import signals to ensure post_migrate seeder runs after migrations
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid raising during manage.py commands where imports may fail
            pass
