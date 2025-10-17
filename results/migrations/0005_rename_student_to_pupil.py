# Generated manually for Student -> Pupil refactoring

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0004_result_result_stud_sess_term_idx_and_more'),
        ('accounts', '0004_rename_studentprofile_to_pupilprofile'),
    ]

    operations = [
        # Rename student field to pupil in Result model
        migrations.RenameField(
            model_name='result',
            old_name='student',
            new_name='pupil',
        ),
        # Rename student field to pupil in ResultSummary model
        migrations.RenameField(
            model_name='resultsummary',
            old_name='student',
            new_name='pupil',
        ),
        # Rename indexes in Result
        migrations.RenameIndex(
            model_name='result',
            new_name='result_pupil_sess_term_idx',
            old_name='result_stud_sess_term_idx',
        ),
        migrations.RenameIndex(
            model_name='result',
            new_name='result_pupil_idx',
            old_name='result_student_idx',
        ),
        # Rename indexes in ResultSummary
        migrations.RenameIndex(
            model_name='resultsummary',
            new_name='summary_pupil_sess_term_idx',
            old_name='summary_stud_sess_term_idx',
        ),
        migrations.RenameIndex(
            model_name='resultsummary',
            new_name='summary_pupil_idx',
            old_name='summary_student_idx',
        ),
    ]
