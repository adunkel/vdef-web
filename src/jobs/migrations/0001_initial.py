# Generated by Django 2.1.5 on 2019-03-05 20:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('jobid', models.CharField(max_length=50)),
                ('color', models.CharField(blank=True, max_length=20)),
                ('value', models.IntegerField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to='')),
                ('para1name', models.CharField(blank=True, max_length=20)),
                ('para2name', models.CharField(blank=True, max_length=20)),
                ('para1value', models.IntegerField(blank=True)),
                ('para2value', models.IntegerField(blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]