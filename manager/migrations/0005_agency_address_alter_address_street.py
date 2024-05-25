# Generated by Django 5.0.3 on 2024-05-03 11:56

import django.db.models.deletion
from django.db import migrations, models

import manager.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0004_alter_address_entrance_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='address',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='manager.address', verbose_name='address'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='street',
            field=models.CharField(max_length=255, validators=[manager.validators.street_name_validator], verbose_name='street name'),
        ),
    ]
