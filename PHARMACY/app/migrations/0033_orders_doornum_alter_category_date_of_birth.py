# Generated by Django 4.2.4 on 2023-10-08 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_category_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='doornum',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='category',
            name='date_of_birth',
            field=models.DateField(blank=True, default=1),
        ),
    ]
