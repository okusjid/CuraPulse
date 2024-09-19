from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from ..models import CustomUser, Appointment, MedicalRecord
from django.utils.dateparse import parse_date
from django.core.cache import cache
from django.db.models import Count
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

# Admin Dashboard View
class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    A view for displaying the admin dashboard. Only accessible to admin users.
    Shows a summary of doctors, patients, appointments, and medical records.
    """
    template_name = 'accounts/admin.html'

    def test_func(self):
        """Ensure the user is authenticated and is an admin."""
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def handle_no_permission(self):
        """Redirect to login page if user is not an admin."""
        return redirect('login')

    def get_context_data(self, **kwargs):
        """
        Pass the required context data to the dashboard template, including:
        - List of doctors
        - List of patients
        - List of appointments
        - List of medical records
        """
        context = super().get_context_data(**kwargs)
        try:
            context['doctors'] = CustomUser.objects.filter(role='doctor')
            context['patients'] = CustomUser.objects.filter(role='patient')
            context['appointments'] = Appointment.objects.all()
            context['records'] = MedicalRecord.objects.all()
        except Exception as e:
            logger.error(f"Error retrieving dashboard data: {e}")
            context['error'] = 'Unable to load dashboard data. Please try again later.'
        return context

admin_dashboard = AdminDashboardView.as_view()

# AdminRequiredMixin for views that require admin access
class AdminRequiredMixin(UserPassesTestMixin):
    """
    A mixin to ensure that only admin users can access certain views.
    """

    def test_func(self):
        """Ensure the user is authenticated and is an admin."""
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def handle_no_permission(self):
        """Redirect to the login page if the user is not an admin."""
        return redirect('login')

admin_required = AdminRequiredMixin


class AdminAppointmentReportView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    A view for displaying a report of appointments. Only accessible to admins.
    Supports filtering by start date, end date, status, and doctor's name.
    """
    model = Appointment
    template_name = 'accounts/appointment_report.html'
    context_object_name = 'appointments'
    paginate_by = 10

    def test_func(self):
        """Ensure that only admins can access this view."""
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def get_queryset(self):
        """
        Get the filtered list of appointments based on query parameters.
        Results are cached to improve performance.
        Filters:
        - Start date
        - End date
        - Status
        - Doctor name
        """
        start_date = self.request.GET.get('start_date', '')
        end_date = self.request.GET.get('end_date', '')
        status = self.request.GET.get('status', '')
        doctor_name = self.request.GET.get('doctor', '')
        cache_key = f'appointment_report_{start_date}_{end_date}_{status}_{doctor_name}'

        queryset = cache.get(cache_key)

        if queryset is None:
            try:
                queryset = Appointment.objects.all()

                if start_date:
                    queryset = queryset.filter(scheduled_at__date__gte=parse_date(start_date))
                if end_date:
                    queryset = queryset.filter(scheduled_at__date__lte=parse_date(end_date))
                if status:
                    queryset = queryset.filter(status=status)
                if doctor_name:
                    queryset = queryset.filter(doctor__full_name__icontains=doctor_name)

                # Cache the queryset for 60 seconds
                cache.set(cache_key, queryset, timeout=60)
            except Exception as e:
                logger.error(f"Error retrieving appointments: {e}")
                queryset = Appointment.objects.none()  # Return empty queryset if error occurs

        return queryset

    def get_context_data(self, **kwargs):
        """
        Pass additional context data, including:
        - Start date
        - End date
        - Status filter
        - Doctor filter
        - Daily appointment counts within the date range
        """
        context = super().get_context_data(**kwargs)
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['status'] = self.request.GET.get('status', '')
        context['doctor'] = self.request.GET.get('doctor', '')

        try:
            start_date = parse_date(context['start_date'])
            end_date = parse_date(context['end_date'])
            if start_date and end_date:
                date_range = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
                daily_counts = (Appointment.objects
                                .filter(scheduled_at__date__range=(start_date, end_date))
                                .values('scheduled_at__date')
                                .annotate(count=Count('id'))
                                .order_by('scheduled_at__date'))
                counts_dict = {entry['scheduled_at__date']: entry['count'] for entry in daily_counts}
                context['daily_counts'] = [{'date': date, 'count': counts_dict.get(date, 0)} for date in date_range]
        except Exception as e:
            logger.error(f"Error calculating daily appointment counts: {e}")
            context['daily_counts'] = []  # Provide an empty list in case of error

        return context

admin_appointment_report_view = AdminAppointmentReportView.as_view()

# Doctor Management View (for Admin)
# class AdminDoctorListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
#     """
#     A view for admins to manage the list of doctors. 
#     Allows filtering by search query and specialization.
#     """
#     model = CustomUser
#     template_name = 'accounts/doctor_list.html'
#     context_object_name = 'doctors'
#     paginate_by = 10

#     def get_queryset(self):
#         """Filter doctors based on search and specialization."""
#         queryset = CustomUser.objects.filter(role='doctor')

#         search_query = self.request.GET.get('search', '')
#         if search_query:
#             queryset = queryset.filter(full_name__icontains=search_query)

#         specialization_filter = self.request.GET.get('specialization', '')
#         if specialization_filter:
#             queryset = queryset.filter(specialization__icontains=specialization_filter)

#         return queryset

#     def get_context_data(self, **kwargs):
#         """Pass search and specialization filters to the context."""
#         context = super().get_context_data(**kwargs)
#         context['search_query'] = self.request.GET.get('search', '')
#         context['specialization_filter'] = self.request.GET.get('specialization', '')
#         return context

# admin_doctor_list_view = AdminDoctorListView.as_view()

# Patient Management View (for Admin)
# class AdminPatientListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
#     """
#     A view for admins to manage the list of patients.
#     Allows filtering by search query and gender.
#     """
#     model = CustomUser
#     template_name = 'patients/patient_list.html'
#     context_object_name = 'patients'
#     paginate_by = 10

#     def get_queryset(self):
#         """Filter patients based on search and gender."""
#         queryset = CustomUser.objects.filter(role='patient')

#         search_query = self.request.GET.get('search', '')
#         if search_query:
#             queryset = queryset.filter(full_name__icontains=search_query)

#         gender_filter = self.request.GET.get('gender', '')
#         if gender_filter:
#             queryset = queryset.filter(gender__icontains=gender_filter)

#         return queryset

#     def get_context_data(self, **kwargs):
#         """Pass search and gender filters to the context."""
#         context = super().get_context_data(**kwargs)
#         context['search_query'] = self.request.GET.get('search', '')
#         context['gender_filter'] = self.request.GET.get('gender', '')
#         return context

# admin_patient_list_view = AdminPatientListView.as_view()

# Appointment Management View (for Admin)
# class AdminAppointmentListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
#     """
#     A view for admins to manage the list of appointments.
#     Allows filtering by doctor and patient names.
#     """
#     model = Appointment
#     template_name = 'appointments/appointment_list.html'
#     context_object_name = 'appointments'
#     paginate_by = 10

#     def get_queryset(self):
#         """Optionally filter appointments by doctor or patient."""
#         queryset = Appointment.objects.all()

#         doctor_filter = self.request.GET.get('doctor', '')
#         if doctor_filter:
#             queryset = queryset.filter(doctor__full_name__icontains=doctor_filter)

#         patient_filter = self.request.GET.get('patient', '')
#         if patient_filter:
#             queryset = queryset.filter(patient__full_name__icontains(patient_filter)

#         return queryset

#     def get_context_data(self, **kwargs):
#         """Pass doctor and patient filters to the context."""
#         context = super().get_context_data(**kwargs)
#         context['doctor_filter'] = self.request.GET.get('doctor', '')
#         context['patient_filter'] = self.request.GET.get('patient', '')
#         return context

# admin_appointment_list_view = AdminAppointmentListView.as_view()
