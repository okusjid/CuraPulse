from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
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
class DoctorListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 10  # Optional: For pagination

    def get_queryset(self):
        queryset = super().get_queryset().filter(role='doctor')

        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(full_name__icontains=search_query)

        # Apply specialization filter
        specialization_filter = self.request.GET.get('specialization', '')
        if specialization_filter:
            queryset = queryset.filter(specialization__icontains=specialization_filter)

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
        # Fetch the doctor object based on the primary key (pk)
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='doctor')

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

    def form_valid(self, form):
        """Handle form submission for creating or updating a doctor."""
        doctor_profile = form.save(commit=False)
        doctor_profile.role = 'doctor'  # Ensure role is set to 'doctor'
        doctor_profile.save()
        return redirect('doctor_list_view')

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

delete_doctor_view = DeleteDoctorView.as_view()
