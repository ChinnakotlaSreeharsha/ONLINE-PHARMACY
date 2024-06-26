# Generated by Django 4.2.4 on 2024-01-31 07:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0036_alter_guest_district_alter_guest_state_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('dob', models.DateField(blank=True, null=True)),
                ('weight', models.IntegerField()),
                ('contact', models.CharField(max_length=10)),
                ('address', models.CharField(max_length=250)),
                ('landmark', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('state', models.CharField(max_length=20)),
                ('pincode', models.CharField(max_length=6)),
                ('email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Personal Info',
                'verbose_name_plural': 'Personal Info',
            },
        ),
    ]
