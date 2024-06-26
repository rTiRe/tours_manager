# Generated by Django 4.2.4 on 2024-05-04 11:24

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0013_city_point'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='point',
            field=django.contrib.gis.db.models.fields.PointField(default=None, srid=4326, verbose_name='address geopoint'),
            preserve_default=False,
        ),
    ]
