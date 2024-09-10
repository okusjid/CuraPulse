from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction  # Import transaction handling
from ..models import CustomUser, Appointment, MedicalRecord
from ..forms import DoctorProfileForm

# Doctor Dashboard View
class DoctorDashboardView(LoginRequiredMixin, View):
    template_name = 'doctors/doctor-info.html'

    def get(self, request, doctor_id=None):
        user_id = doctor_id or request.GET.get('user_id')
        doctor_user = get_object_or_404(CustomUser, id=user_id)
        appointments_with_records = []

        # Fetch appointments for the doctor
        appointment_info = Appointment.objects.filter(doctor=doctor_user)

        for appointment in appointment_info:
            # Fetch records associated with each appointment
            records = MedicalRecord.objects.filter(appointment=appointment)
            appointments_with_records.append({
                'appointment': appointment,
                'records': records
            })

        return render(request, self.template_name, {
            'doctor_user': doctor_user,
            'appointments_with_records': appointments_with_records,
        })

doctor_dashboard = DoctorDashboardView.as_view()

# Doctor List View (Admin only)
from django.core.cache import cache

class DoctorListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        specialization_filter = self.request.GET.get('specialization', '')

        # Create a unique cache key based on the filters
        cache_key = f'doctor_list_{search_query}_{specialization_filter}'
        cached_queryset = cache.get(cache_key)

        if cached_queryset:
            return cached_queryset

        queryset = super().get_queryset().filter(role='doctor')

        if search_query:
            queryset = queryset.filter(full_name__icontains=search_query)

        if specialization_filter:
            queryset = queryset.filter(specialization__icontains=specialization_filter)

        # Cache the queryset for 5 minutes
        cache.set(cache_key, queryset, timeout=300)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_name'] = "Doctor's List"
        context['search_query'] = self.request.GET.get('search', '')
        context['specialization_filter'] = self.request.GET.get('specialization', '')
        return context

doctor_list_view = DoctorListView.as_view()

# Doctor Detail View
class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/doctor_detail.html'
    context_object_name = 'doctor'

    def get_object(self):
        pk = self.kwargs.get('pk')

        # Try to get cached doctor details
        cache_key = f'doctor_detail_{pk}'
        cached_doctor = cache.get(cache_key)

        if cached_doctor:
            return cached_doctor

        doctor = get_object_or_404(CustomUser, pk=pk, role='doctor')

        # Cache the doctor details for 10 minutes
        cache.set(cache_key, doctor, timeout=600)

        return doctor


doctor_detail_view = DoctorDetailView.as_view()

# Create/Update Doctor Profile View
class CreateUpdateDoctorView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = DoctorProfileForm
    template_name = 'accounts/doctor_form.html'
    context_object_name = 'doctor'

    def get_object(self, queryset=None):
        """Retrieve the doctor object for updating, or return None for creating."""
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(CustomUser, pk=pk, role='doctor')
        return None  # For creating a new doctor

    @transaction.atomic  # Ensure atomicity during the create/update operation
    def form_valid(self, form):
        """Handle form submission for creating or updating a doctor."""
        try:
            with transaction.atomic():
                doctor_profile = form.save(commit=False)
                doctor_profile.role = 'doctor'  # Ensure role is set to 'doctor'
                doctor_profile.save()
            return redirect('doctor_list_view')
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

create_update_doctor_view = CreateUpdateDoctorView.as_view()

# Delete Doctor View (Admin only)
class DeleteDoctorView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/doctor_confirm_delete.html'
    context_object_name = 'doctor'
    success_url = reverse_lazy('doctor_list_view')  # Redirect to doctor list after deletion

    def get_object(self, queryset=None):
        """Retrieve the doctor object to delete."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='doctor')

    @transaction.atomic  # Ensure atomicity during the delete operation
    def delete(self, request, *args, **kwargs):
        """Delete the doctor within a transaction."""
        try:
            with transaction.atomic():
                return super().delete(request, *args, **kwargs)
        except Exception as e:
            # Handle exceptions, redirect to error page, or show an error message
            return redirect('doctor_list_view')

delete_doctor_view = DeleteDoctorView.as_view()
