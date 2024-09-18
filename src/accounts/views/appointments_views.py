# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from django.shortcuts import get_object_or_404
# from ..models import Appointment
# from ..serializers import AppointmentSerializer

# class AppointmentListCreateAPIView(APIView):
#     def get(self, request):
#         appointments = Appointment.objects.all()
#         serializer = AppointmentSerializer(appointments, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = AppointmentSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# # Appointment_List_CreateAPIView = AppointmentListCreateAPIView.as_view()


# class AppointmentDetailAPIView(APIView):
#     def get(self, request, pk):
#         appointment = get_object_or_404(Appointment, pk=pk)
#         serializer = AppointmentSerializer(appointment)
#         return Response(serializer.data)

#     def put(self, request, pk):
#         appointment = get_object_or_404(Appointment, pk=pk)
#         serializer = AppointmentSerializer(appointment, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk):
#         appointment = get_object_or_404(Appointment, pk=pk)
#         appointment.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# # Appointment_Detail_APIView=AppointmentDetailAPIView.as_view()



from rest_framework import generics
from ..models import Appointment
from ..serializers import AppointmentSerializer
from rest_framework.authentication import TokenAuthentication
from ..permissions import IsSuperAdmin


class AppointmentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsSuperAdmin]  # Only superusers can access

# class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Appointment.objects.all()
#     serializer_class = AppointmentSerializer
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsSuperAdmin]  # Only superusers can access

from rest_framework import status
from rest_framework.response import Response

class AppointmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsSuperAdmin]

    def put(self, request, *args, **kwargs):
        """Handle updating an appointment (PUT method)."""
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Handle deleting an appointment (DELETE method)."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
