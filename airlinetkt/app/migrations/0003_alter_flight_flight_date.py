# Generated by Django 5.1.3 on 2025-01-20 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_date_flight_flight_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flight',
            name='flight_date',
            field=models.DateTimeField(),
        ),
    ]
