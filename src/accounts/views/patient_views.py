from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import transaction
from ..models import CustomUser
from ..forms import PatientProfileForm
from django.core.cache import cache
import logging

# Set up logging
logger = logging.getLogger(__name__)

class PatientListView(LoginRequiredMixin, ListView):
    """
    View to list all patients with optional search and gender filtering. 
    Results are cached to reduce database load and improve performance.
    """
    model = CustomUser
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 10  # Optional pagination setting

    def get_queryset(self):
        """
        Retrieves and returns a queryset of patients filtered by search query 
        and gender, if provided. Results are cached.
        """
        search_query = self.request.GET.get('search', '')
        gender_filter = self.request.GET.get('gender', '')
        cache_key = f'patient_list_{search_query}_{gender_filter}'

        queryset = cache.get(cache_key)

        if queryset is None:
            try:
                queryset = CustomUser.objects.filter(role='patient')

                if search_query:
                    queryset = queryset.filter(full_name__icontains=search_query)

                if gender_filter:
                    queryset = queryset.filter(gender__icontains=gender_filter)

                queryset = queryset.order_by('full_name')  # Adjust ordering as needed
                cache.set(cache_key, queryset, timeout=60)

            except Exception as e:
                logger.error(f"Error retrieving patient list: {e}")
                queryset = CustomUser.objects.none()  # Return an empty queryset on error

        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds extra context to the template, including search query and 
        gender filter values for form repopulation.
        """
        context = super().get_context_data(**kwargs)
        context['list_name'] = "Patient's List"
        context['search_query'] = self.request.GET.get('search', '')
        context['gender_filter'] = self.request.GET.get('gender', '')
        return context

patient_list_view = PatientListView.as_view()

class PatientDetailView(LoginRequiredMixin, DetailView):
    """
    View to display the details of a specific patient.
    """
    model = CustomUser
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

    def get_object(self):
        """
        Retrieves the patient object based on the primary key provided in the URL.
        """
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='patient')

patient_detail_view = PatientDetailView.as_view()

class CreateUpdatePatientView(LoginRequiredMixin, CreateView, UpdateView):
    """
    View for creating or updating a patient's profile. Handles both the creation
    of new patients and the update of existing patient information.
    """
    model = CustomUser
    form_class = PatientProfileForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list_view')  # Redirect to the patient list view

    def get_object(self, queryset=None):
        """
        Retrieves the patient object if updating. Returns None if creating a new patient.
        """
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(CustomUser, pk=pk, role='patient')
        return None  # For creating a new patient

    @transaction.atomic
    def form_valid(self, form):
        """
        Processes the form submission to either create or update a patient's profile. 
        Ensures the transaction is atomic to prevent partial updates.
        """
        try:
            patient_profile = form.save(commit=False)
            patient_profile.role = 'patient'  # Ensure the role is set to 'patient'
            patient_profile.save()
            return super().form_valid(form)
        except Exception as e:
            logger.error(f"Error saving patient profile: {e}")
            form.add_error(None, "An error occurred while saving the patient profile.")
            return self.form_invalid(form)

create_update_patient_view = CreateUpdatePatientView.as_view()

class DeletePatientView(LoginRequiredMixin, DeleteView):
    """
    View to delete a specific patient. Provides confirmation before deletion.
    """
    model = CustomUser
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list_view')  # Redirect to patient list view after deletion

    def get_object(self, queryset=None):
        """
        Retrieves the patient object based on the primary key provided in the URL.
        """
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='patient')

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        """
        Deletes the patient within a transaction to ensure data consistency. 
        Handles exceptions by redirecting to the patient list.
        """
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error deleting patient: {e}")
            # Handle any exceptions, maybe redirect to an error page or show a message
            return redirect('patient_list_view')

delete_patient_view = DeletePatientView.as_view()
