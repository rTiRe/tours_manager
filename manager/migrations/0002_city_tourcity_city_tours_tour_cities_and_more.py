# Generated by Django 5.0.3 on 2024-05-03 06:09

import uuid

import django.db.models.deletion
from django.db import migrations, models

import manager.models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('country', models.CharField(max_length=255, verbose_name='country')),
            ],
            options={
                'verbose_name': 'city',
                'verbose_name_plural': ('cities',),
                'db_table': '"tours_data"."city"',
            },
        ),
        migrations.CreateModel(
            name='TourCity',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.city', verbose_name='city')),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manager.tour', verbose_name='tour')),
            ],
            options={
                'verbose_name': 'relationship tour city',
                'verbose_name_plural': 'relationships tour city',
                'db_table': '"tours_data"."tour_city"',
                'unique_together': {('tour', 'city')},
            },
        ),
        migrations.AddField(
            model_name='city',
            name='tours',
            field=models.ManyToManyField(through='manager.TourCity', to='manager.tour', verbose_name='tours'),
        ),
        migrations.AddField(
            model_name='tour',
            name='cities',
            field=models.ManyToManyField(through='manager.TourCity', to='manager.city', verbose_name='cities'),
        ),
        migrations.AlterUniqueTogether(
            name='city',
            unique_together={('name', 'country')},
        ),
    ]
