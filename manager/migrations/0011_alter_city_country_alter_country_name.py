# Generated by Django 5.0.3 on 2024-05-03 23:10

import django.db.models.deletion
from django.db import migrations, models

import manager.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0010_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.country', verbose_name='country'),
        ),
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(max_length=255, verbose_name='country'),
        ),
    ]
