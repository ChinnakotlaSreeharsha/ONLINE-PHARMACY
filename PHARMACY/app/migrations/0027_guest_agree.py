# Generated by Django 4.2.4 on 2023-09-24 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_guestproducts_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='guest',
            name='agree',
            field=models.BooleanField(default=False),
        ),
    ]
