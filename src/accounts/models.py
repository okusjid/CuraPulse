from time import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    username = models.CharField(max_length=150, unique=True, blank=True, null=True) 
    full_name = models.CharField(max_length=255 , blank= True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    GENDERS = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    gender = models.CharField(max_length=100, choices=GENDERS, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_admin(self):
        return self.role == 'admin'

    def is_doctor(self):
        return self.role == 'doctor'

    def is_patient(self):
        return self.role == 'patient'
    

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments')
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='patient_appointments')
    scheduled_at = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(null=True, blank=True)  # Optional field for extra details
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.doctor.full_name} -> {self.patient.full_name} on {self.scheduled_at.strftime('%Y-%m-%d %H:%M')} ({self.get_status_display()})"

    def is_past_due(self):
        """Check if the appointment is overdue."""
        return self.scheduled_at < timezone.now() and self.status == 'pending'
    
class MedicalRecord(models.Model):
    doctor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='medical_records_as_doctor', 
        limit_choices_to={'role': 'doctor'}
    )
    patient = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='medical_records_as_patient', 
        limit_choices_to={'role': 'patient'}
    )
    appointment = models.ForeignKey(
        Appointment, 
        on_delete=models.CASCADE, 
        related_name='medical_records'
    )
    diagnosis = models.TextField()
    treatment = models.TextField()
    notes = models.TextField(blank=True, null=True)
    report = models.FileField(upload_to='reports/', blank=True, null=True)  # Updated to FileField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical Record for {self.diagnosis} - {self.created_at.strftime('%Y-%m-%d')}"

    def is_doctor(self):
        return self.doctor.role == 'doctor'  # Updated to use doctor relation

    def is_patient(self):
        return self.patient.role == 'patient'  # Updated to use patient relation
