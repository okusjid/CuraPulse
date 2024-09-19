from rest_framework import generics
from ..models import Appointment
from ..serializers import AppointmentSerializer
from rest_framework.authentication import TokenAuthentication
from ..permissions import IsSuperAdmin
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ObjectDoesNotExist

class AppointmentListCreateAPIView(generics.ListCreateAPIView):
    """
    API view to retrieve a list of appointments or create a new appointment.
    
    * Only superusers can access this view.
    * Uses TokenAuthentication for authentication.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSuperAdmin]  # Only superusers can access

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API view to retrieve, update, or delete an appointment.

    * Only superusers can access this view.
    * Uses TokenAuthentication for authentication.
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsSuperAdmin]

    def get_object(self):
        try:
            return super().get_object()
        except ObjectDoesNotExist:
            raise NotFound('Appointment not found')

    def put(self, request, *args, **kwargs):
        """
        Handle updating an appointment (PUT method).
        
        This method allows the superuser to update the details of an existing appointment.
        """
        try:
            return self.update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        """
        Handle deleting an appointment (DELETE method).

        This method allows the superuser to delete an existing appointment.
        Returns a 204 No Content response on successful deletion.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
