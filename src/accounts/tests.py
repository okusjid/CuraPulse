from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Appointment  
from .serializers import AppointmentSerializer

User = get_user_model()

class AppointmentAPITests(APITestCase):

    def setUp(self):
        """
        Set up test environment before each test case. 
        This includes creating a superuser for authentication, setting authorization headers,
        defining the URLs for appointment list and detail views, and creating a sample appointment.
        """
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
        """
        Test creating a new appointment via the API.
        Ensures that the appointment is successfully created with valid data
        and checks if the number of appointments increases.
        """
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
        """
        Test retrieving an existing appointment via the API.
        Verifies that the correct appointment details are returned when accessed.
        """
        response = self.client.get(self.appointment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['notes'], self.appointment.notes)

    def test_update_appointment(self):
        """
        Test updating an existing appointment via the API.
        Checks that the appointment is updated successfully and that the changes are reflected in the database.
        """
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
        """
        Test deleting an existing appointment via the API.
        Ensures that the appointment is deleted successfully and no longer exists in the database.
        """
        response = self.client.delete(self.appointment_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Appointment.objects.count(), 0)  # Check if the appointment was deleted
