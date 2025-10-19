from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
import logging
from django.db import connection

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_default_theme(sender, **kwargs):
    """Ensure a default `theme` SiteSetting exists after migrations.

    This helps deployments where frontend expects a theme record to be present.
    The function is guarded so it does not attempt ORM queries before the
    underlying DB table exists (which causes ProgrammingError during migrate).
    """
    # Only run for the media_manager app or for project-wide migrations
    if sender.name not in ("media_manager", "backend"):
        return

    try:
        SiteSetting = apps.get_model('media_manager', 'SiteSetting')
    except LookupError:
        logger.debug('SiteSetting model not available yet; skipping seeder')
        return

    # Guard: ensure the underlying table exists before performing ORM queries.
    try:
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names(cursor)
    except Exception:
        logger.exception('Failed to introspect database tables; skipping SiteSetting seeder')
        return

    table_name = SiteSetting._meta.db_table
    if table_name not in tables:
        logger.debug('Table %s does not exist yet; skipping SiteSetting seeder', table_name)
        return

    try:
        obj, created = SiteSetting.objects.get_or_create(
            key='theme',
            defaults={'value': {
                'primary': '#3b82f6',
                'secondary': '#0ea5e9',
                'background': '#0f172a',
                'text': '#e6eef8'
            }}
        )
        if created:
            logger.info('Created default SiteSetting theme')
    except Exception as exc:
        logger.exception('Error while creating default SiteSetting: %s', exc)
