# Generated by Django 4.2.4 on 2024-06-16 14:15

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("manager", "0032_tour_avatar"),
    ]

    operations = [
        migrations.CreateModel(
            name="AgencyRequests",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="manager.account",
                        verbose_name="account",
                    ),
                ),
                (
                    "agency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="manager.agency",
                        verbose_name="agency",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
