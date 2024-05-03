# Generated by Django 5.0.3 on 2024-05-03 08:54

import django.db.models.deletion
import manager.models
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_city_tourcity_city_tours_tour_cities_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='city',
            options={'verbose_name': 'city', 'verbose_name_plural': 'cities'},
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('street', models.CharField(max_length=255, verbose_name='street name')),
                ('house_number', models.CharField(max_length=8, validators=[manager.models.house_number_validator], verbose_name='house number')),
                ('entrance_number', models.SmallIntegerField(verbose_name='entrance number')),
                ('floor', models.SmallIntegerField(verbose_name='floor number')),
                ('flat_number', models.SmallIntegerField(verbose_name='flat number')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.city', verbose_name='city')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]