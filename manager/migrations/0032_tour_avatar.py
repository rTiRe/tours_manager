# Generated by Django 4.1.7 on 2024-06-03 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0031_account_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='covers/', verbose_name='cover'),
        ),
    ]