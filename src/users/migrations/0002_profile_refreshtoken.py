# Generated by Django 2.1.5 on 2019-01-26 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='refreshtoken',
            field=models.CharField(default='default', max_length=50),
            preserve_default=False,
        ),
    ]