# Generated by Django 2.1.5 on 2019-01-28 00:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20190126_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='expiresat',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='timecreated',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
    ]
