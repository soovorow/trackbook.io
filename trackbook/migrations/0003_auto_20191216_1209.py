# Generated by Django 3.0 on 2019-12-16 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trackbook', '0002_app_app_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='platform',
            field=models.CharField(choices=[('I', 'iOS'), ('A', 'Android')], default='I', max_length=1),
        ),
    ]
