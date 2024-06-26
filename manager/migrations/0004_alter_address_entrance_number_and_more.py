# Generated by Django 5.0.3 on 2024-05-03 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0003_alter_city_options_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='entrance_number',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='entrance number'),
        ),
        migrations.AlterField(
            model_name='address',
            name='flat_number',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='flat number'),
        ),
        migrations.AlterField(
            model_name='address',
            name='floor',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='floor number'),
        ),
    ]
