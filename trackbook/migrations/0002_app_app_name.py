# Generated by Django 2.2.7 on 2019-12-08 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackbook', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='app',
            name='app_name',
            field=models.CharField(default='Untitled App', max_length=70),
        ),
    ]
