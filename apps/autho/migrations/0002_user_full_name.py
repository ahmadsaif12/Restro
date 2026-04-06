from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("autho", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="full_name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

