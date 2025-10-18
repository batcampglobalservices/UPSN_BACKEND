from django.core.management.base import BaseCommand
from classes.models import Class

# Map old levels to new levels if possible, or set to None for manual review
def get_new_level(old_level):
    mapping = {
        'JSS1': 'JK1',
        'JSS2': 'JK2',
        'JSS3': 'JK3',
        'SS1': 'SK',
        'SS2': 'GRADE 1',
        'SS3': 'GRADE 2',
        # Add more mappings if needed
    }
    return mapping.get(old_level.upper())

class Command(BaseCommand):
    help = 'Update or delete classes with old levels to match new class level choices.'

    def handle(self, *args, **options):
        updated, deleted = 0, 0
        for c in Class.objects.all():
            new_level = get_new_level(c.level)
            if new_level:
                self.stdout.write(f'Updating class {c.name} from {c.level} to {new_level}')
                c.level = new_level
                c.save()
                updated += 1
            elif c.level not in ['JK1', 'JK2', 'JK3', 'SK', 'GRADE 1', 'GRADE 2', 'GRADE 3', 'GRADE 4', 'GRADE 5']:
                self.stdout.write(f'Deleting class {c.name} with invalid level {c.level}')
                c.delete()
                deleted += 1
        self.stdout.write(self.style.SUCCESS(f'Updated {updated} classes, deleted {deleted} classes.'))
