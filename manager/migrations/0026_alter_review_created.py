# Generated by Django 4.1.7 on 2024-05-27 10:57

import datetime

from django.db import migrations, models

import manager.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0025_review_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 27, 10, 57, 23, 273307, tzinfo=datetime.timezone.utc), validators=[manager.validators.date_validator], verbose_name='creatin date and time'),
        ),
    ]
