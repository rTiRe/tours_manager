# Generated by Django 4.1.7 on 2024-05-25 04:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0022_remove_account_is_agency_account_agency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='agency',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='account', to='manager.agency', verbose_name='agency account'),
        ),
    ]