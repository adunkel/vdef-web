# Generated by Django 2.1.5 on 2019-03-28 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0006_job_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='picture',
            field=models.ImageField(default='job_pictures/default.jpg', upload_to='job_pictures'),
        ),
    ]
