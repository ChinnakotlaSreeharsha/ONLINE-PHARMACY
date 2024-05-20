# Generated by Django 4.2.4 on 2023-09-17 02:53

import app.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0006_cart'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrescriptiveCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=app.models.getPrescriptionCartFileName)),
                ('approve', models.CharField(blank=True, choices=[('Approved', 'Approved'), ('Processing', 'Processing'), ('Declined', 'Declined')], default=('Processing', 'Processing'), max_length=50, null=True)),
                ('product_qty', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]


























