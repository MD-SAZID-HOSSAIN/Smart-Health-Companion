from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mainapp", "0007_doctor"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctor",
            name="is_published",
            field=models.BooleanField(default=True),
        ),
    ]


