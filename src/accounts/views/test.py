# # accounts/tests/test_api.py

# from django.test import TestCase
# from django.urls import reverse
# from rest_framework.authtoken.models import Token
# from accounts.models import CustomUser, Appointment

# class AppointmentAPITests(TestCase):

#     def setUp(self):
#         # Create a superuser for authentication
#         self.superuser = CustomUser.objects.create_superuser(
#             username='admin',
#             password='password123',
#             email='admin@example.com'
#         )
#         self.token = Token.objects.create(user=self.superuser)

#         # URL for Appointment API
#         self.appointment_list_url = reverse('appointment-list-create')  # Replace with your URL name
#         self.appointment_detail_url = reverse('appointment-detail', kwargs={'pk': 1})  # Replace with your URL name

#         # Create a sample appointment
#         self.appointment = Appointment.objects.create(
#             doctor=self.superuser,
#             patient=self.superuser,  # Adjust based on your test case
#             scheduled_at='2024-09-18T10:00:00Z',  # Example datetime
#             status='pending'
#         )

#     def test_create_appointment(self):
#         """Test creating a new appointment."""
#         response = self.client.post(
#             self.appointment_list_url,
#             {
#                 'doctor': self.superuser.id,
#                 'patient': self.superuser.id,
#                 'scheduled_at': '2024-09-18T10:00:00Z',
#                 'status': 'pending',
#             },
#             HTTP_AUTHORIZATION=f'Token {self.token.key}'  # Include token for authentication
#         )
#         self.assertEqual(response.status_code, 201)  # Check if appointment was created

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from ..models import Appointment  # Adjust the import based on your app structure
from ..serializers import AppointmentSerializer

User = get_user_model()

class AppointmentAPITests(APITestCase):

    def setUp(self):
        # Create a superuser for authentication
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='password123',
            email='admin@example.com'
        )
        self.token = Token.objects.create(user=self.superuser)

        # Set the Authorization header for authenticated requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # URL for Appointment API
        self.appointment_list_url = reverse('appointment-list-create')  # Replace with your URL name
        self.appointment_detail_url = reverse('appointment-detail', kwargs={'pk': 1})  # Replace with your URL name

        # Create a sample appointment
        self.appointment = Appointment.objects.create(
            doctor=self.superuser,
            patient=self.superuser,  # You might want to create a different user for patient
            scheduled_at='2024-09-25T15:00:00Z',
            status='pending',
            notes='Initial appointment'
        )

    def test_create_appointment(self):
        """Test creating a new appointment."""
        data = {
            'doctor': self.superuser.id,
            'patient': self.superuser.id,  # Change to an actual patient user
            'scheduled_at': '2024-09-25T15:00:00Z',
            'status': 'pending',
            'notes': 'New appointment test'
        }
        response = self.client.post(self.appointment_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)  # Check if the appointment was created
        self.assertEqual(Appointment.objects.get(id=2).notes, 'New appointment test')

    def test_retrieve_appointment(self):
        """Test retrieving an existing appointment."""
        response = self.client.get(self.appointment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], self.appointment.notes)

    def test_update_appointment(self):
        """Test updating an existing appointment."""
        data = {
            'notes': 'Updated appointment notes'
        }
        response = self.client.put(self.appointment_detail_url, data)

        # Check if the response is as expected
        print(response.data)  # Print to see if there are validation errors or other issues

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.notes, 'Updated appointment notes')


    def test_delete_appointment(self):
        """Test deleting an existing appointment."""
        response = self.client.delete(self.appointment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)  # Check if the appointment was deleted
