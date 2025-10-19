# Generated manual migration to add SiteSetting model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("media_manager", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteSetting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("key", models.CharField(max_length=100, unique=True)),
                ("value", models.JSONField(default=dict, blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["key"],
            },
        ),
    ]
