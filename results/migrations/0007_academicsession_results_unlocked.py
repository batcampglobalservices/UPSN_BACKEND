from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0006_remove_result_result_pupil_sess_term_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='academicsession',
            name='results_unlocked',
            field=models.BooleanField(default=False, help_text='If true, pupils can view results immediately regardless of release date'),
        ),
    ]
