from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0002_class_class_level_idx_class_class_teacher_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='level',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('JK1', 'JK1'),
                    ('JK2', 'JK2'),
                    ('JK3', 'JK3'),
                    ('SK', 'SK'),
                    ('GRADE 1', 'GRADE 1'),
                    ('GRADE 2', 'GRADE 2'),
                    ('GRADE 3', 'GRADE 3'),
                    ('GRADE 4', 'GRADE 4'),
                    ('GRADE 5', 'GRADE 5'),
                ]
            ),
        ),
        migrations.AlterField(
            model_name='class',
            name='name',
            field=models.CharField(max_length=50, unique=True, help_text='e.g., JK1A, GRADE 2B'),
        ),
    ]
