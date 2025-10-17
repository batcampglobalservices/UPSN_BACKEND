# Generated manually for Student -> Pupil refactoring

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_customuser_user_role_idx_customuser_user_active_idx_and_more'),
    ]

    operations = [
        # Rename the StudentProfile model to PupilProfile
        migrations.RenameModel(
            old_name='StudentProfile',
            new_name='PupilProfile',
        ),
        # Rename the student_class field to pupil_class
        migrations.RenameField(
            model_name='pupilprofile',
            old_name='student_class',
            new_name='pupil_class',
        ),
        # Rename indexes
        migrations.RenameIndex(
            model_name='pupilprofile',
            new_name='pupil_class_idx',
            old_name='student_class_idx',
        ),
        migrations.RenameIndex(
            model_name='pupilprofile',
            new_name='pupil_user_idx',
            old_name='student_user_idx',
        ),
    ]
