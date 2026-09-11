from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("simulations", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="simulationrun",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("SUCCESS", "Success"),
                    ("FAILURE", "Failure"),
                    ("TIMED_OUT", "Timed Out"),
                ],
                default="PENDING",
                max_length=10,
            ),
        ),
    ]
