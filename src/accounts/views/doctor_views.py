from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from ..models import CustomUser, Appointment, MedicalRecord
from ..forms import DoctorProfileForm
from django.core.cache import cache

# Doctor Dashboard View
class DoctorDashboardView(LoginRequiredMixin, View):
    """
    View for the doctor's dashboard, displaying doctor information and their appointments.
    """
    template_name = 'doctors/doctor-info.html'

    def get(self, request, doctor_id=None):
        try:
            user_id = doctor_id or request.GET.get('user_id')
            doctor_user = get_object_or_404(CustomUser, id=user_id)
            appointments_with_records = []

            # Fetch appointments for the doctor
            appointment_info = Appointment.objects.filter(doctor=doctor_user)

            for appointment in appointment_info:
                records = MedicalRecord.objects.filter(appointment=appointment)
                appointments_with_records.append({
                    'appointment': appointment,
                    'records': records
                })

            return render(request, self.template_name, {
                'doctor_user': doctor_user,
                'appointments_with_records': appointments_with_records,
            })
        except Exception as e:
            # Log the error or handle it appropriately
            return render(request, self.template_name, {'error': 'Error fetching doctor information.'})

doctor_dashboard = DoctorDashboardView.as_view()


class DoctorListView(LoginRequiredMixin, ListView):
    """
    View to list all doctors with optional search and filtering.
    """
    model = CustomUser
    template_name = 'accounts/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 5  # Optional: For pagination

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        specialization_filter = self.request.GET.get('specialization', '')
        cache_key = f'doctor_list_{search_query}_{specialization_filter}'

        try:
            queryset = cache.get(cache_key)

            if queryset is None:
                queryset = CustomUser.objects.filter(role='doctor')

                if search_query:
                    queryset = queryset.filter(full_name__icontains=search_query)

                if specialization_filter:
                    queryset = queryset.filter(specialization__icontains=specialization_filter)

                queryset = queryset.order_by('full_name')  # Adjust ordering as needed
                cache.set(cache_key, queryset, timeout=30)

            return queryset
        except Exception as e:
            # Handle caching errors or log as needed
            return CustomUser.objects.filter(role='doctor')  # Fallback to default queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_name'] = "Doctor's List"
        context['search_query'] = self.request.GET.get('search', '')
        context['specialization_filter'] = self.request.GET.get('specialization', '')
        return context

doctor_list_view = DoctorListView.as_view()


class DoctorDetailView(LoginRequiredMixin, DetailView):
    """
    View to display details of a specific doctor.
    """
    model = CustomUser
    template_name = 'accounts/doctor_detail.html'
    context_object_name = 'doctor'

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            return get_object_or_404(CustomUser, pk=pk, role='doctor')
        except Exception as e:
            # Log the error or handle it appropriately
            return None  # Handle this case in the template

doctor_detail_view = DoctorDetailView.as_view()


class CreateUpdateDoctorView(LoginRequiredMixin, UpdateView):
    """
    View for creating or updating a doctor's profile.
    """
    model = CustomUser
    form_class = DoctorProfileForm
    template_name = 'accounts/doctor_form.html'
    context_object_name = 'doctor'

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(CustomUser, pk=pk, role='doctor')
        return None  # For creating a new doctor

    @transaction.atomic  # Ensure atomicity during the create/update operation
    def form_valid(self, form):
        try:
            doctor_profile = form.save(commit=False)
            doctor_profile.role = 'doctor'  # Ensure role is set to 'doctor'
            doctor_profile.save()
            return redirect('doctor_list_view')
        except Exception as e:
            form.add_error(None, 'An error occurred while saving the profile.')
            return self.form_invalid(form)

create_update_doctor_view = CreateUpdateDoctorView.as_view()


class DeleteDoctorView(LoginRequiredMixin, DeleteView):
    """
    View to delete a doctor's profile.
    """
    model = CustomUser
    template_name = 'accounts/doctor_confirm_delete.html'
    context_object_name = 'doctor'
    success_url = reverse_lazy('doctor_list_view')

    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='doctor')

    @transaction.atomic  # Ensure atomicity during the delete operation
    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            # Handle deletion errors
            return redirect('doctor_list_view')  # Redirect to the list view or show an error message

delete_doctor_view = DeleteDoctorView.as_view()
