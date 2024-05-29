# Generated by Django 4.1.7 on 2024-05-27 10:56

import datetime
from django.db import migrations, models
import manager.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0024_alter_review_tour'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 27, 10, 56, 1, 414022), validators=[manager.validators.date_validator], verbose_name='creatin date and time'),
        ),
    ]