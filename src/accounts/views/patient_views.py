from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ..models import CustomUser
from ..forms import PatientProfileForm

# Patient List View (Admin only)
class PatientListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 10  # Optional: For pagination

    def get_queryset(self):
        """Override to filter patients based on search query and gender filter."""
        queryset = CustomUser.objects.filter(role='patient')

        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(full_name__icontains=search_query)

        # Apply gender filter
        gender_filter = self.request.GET.get('gender', '')
        if gender_filter:
            queryset = queryset.filter(gender__icontains=gender_filter)

        return queryset

    def get_context_data(self, **kwargs):
        """Add additional context variables."""
        context = super().get_context_data(**kwargs)
        context['list_name'] = "Patient's List"
        context['search_query'] = self.request.GET.get('search', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        return context

patient_list_view = PatientListView.as_view()

# Patient Detail View
class PatientDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

    def get_object(self):
        """Override to get the patient object by primary key."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='patient')

patient_detail_view = PatientDetailView.as_view()

# Create/Update Patient Profile View
class CreateUpdatePatientView(LoginRequiredMixin, CreateView, UpdateView):
    model = CustomUser
    form_class = PatientProfileForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list_view')  # Redirect to patient list view

    def get_object(self, queryset=None):
        """Get the patient object based on the primary key for updating."""
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(CustomUser, pk=pk, role='patient')
        return None  # For creating a new patient

    def form_valid(self, form):
        """Handle the valid form submission."""
        patient_profile = form.save(commit=False)
        patient_profile.role = 'patient'  # Ensure the role is set to 'patient'
        patient_profile.save()
        return super().form_valid(form)

create_update_patient_view = CreateUpdatePatientView.as_view()

# Delete Patient View
class DeletePatientView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list_view')  # Redirect to patient list view after deletion

    def get_object(self, queryset=None):
        """Get the patient object based on the primary key."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='patient')

delete_patient_view = DeletePatientView.as_view()
