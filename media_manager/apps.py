from django.apps import AppConfig
import logging


class MediaManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'media_manager'
    verbose_name = 'Media Manager'

    def ready(self):
        # Import signal handlers to register post_migrate seeder
        try:
            from . import signals  # noqa: F401
        except Exception:
            # Avoid breaking startup if signals import fails; log for debugging
            logging.getLogger(__name__).exception('Failed to import media_manager signals')
