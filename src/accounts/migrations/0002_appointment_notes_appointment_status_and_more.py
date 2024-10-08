# Generated by Django 5.1.1 on 2024-09-10 12:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='medicalrecord',
            name='doctor',
            field=models.ForeignKey(limit_choices_to={'role': 'doctor'}, on_delete=django.db.models.deletion.CASCADE, related_name='medical_records_as_doctor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='medicalrecord',
            name='patient',
            field=models.ForeignKey(limit_choices_to={'role': 'patient'}, on_delete=django.db.models.deletion.CASCADE, related_name='medical_records_as_patient', to=settings.AUTH_USER_MODEL),
        ),
    ]
