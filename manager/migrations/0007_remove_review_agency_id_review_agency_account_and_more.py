# Generated by Django 5.0.3 on 2024-05-03 19:23

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0006_review'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='agency_id',
        ),
        migrations.AddField(
            model_name='review',
            name='agency',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='manager.agency', verbose_name='agency'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name=True)),
            ],
            options={
                'verbose_name': 'account',
                'verbose_name_plural': 'accounts',
                'db_table': '"tours_data"."account"',
            },
        ),
        migrations.AddField(
            model_name='review',
            name='account',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='manager.account', verbose_name='account'),
            preserve_default=False,
        ),
    ]