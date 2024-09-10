from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse, reverse_lazy
from .models import CustomUser, Appointment, MedicalRecord
from .forms import LoginForm, DoctorProfileForm, CreateRecordForm, PatientProfileForm
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LogoutView
from django.db import transaction
from django.contrib.auth import authenticate, login


class UserLoginView(View):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get(self, request): 
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Use transaction.atomic() to ensure the login process is atomic
            with transaction.atomic():
                user = authenticate(request, username=username, password=password)
                print(username, password)
                print(user)

                if user is not None:
                    login(request, user)
                    if user.is_superuser:
                        return redirect('/admin')
                    elif hasattr(user, 'is_admin') and user.is_admin():  # Adjusted for potential method
                        return redirect('admin_dashboard')
                    elif hasattr(user, 'is_doctor') and user.is_doctor():
                        return redirect(reverse('doctor_dashboard') + f'?user_id={user.id}')
                else:
                    return render(request, self.template_name, {'form': form, 'error': 'Invalid credentials'})

        return render(request, self.template_name, {'form': form})

# Keeping the original function name intact to maintain sync
user_login = UserLoginView.as_view()



class DoctorDashboardView(LoginRequiredMixin, View):
    template_name = 'doctors/doctor-info.html'

    def get(self, request, doctor_id=None):
        user_id = doctor_id if doctor_id else request.GET.get('user_id')
        doctor_user = None
        appointments_with_records = []

        if user_id:
            try:
                doctor_user = get_object_or_404(CustomUser, id=user_id)
                print("User object is", doctor_user)

                # Wrap read operations in a transaction if needed in the future
                with transaction.atomic():
                    appointment_info = Appointment.objects.filter(doctor=doctor_user)
                    print(appointment_info)

                    for appointment in appointment_info:
                        records = MedicalRecord.objects.filter(appointment=appointment)
                        appointments_with_records.append({
                            'appointment': appointment,
                            'records': records
                        })

            except CustomUser.DoesNotExist:
                return redirect('user_login')

        return render(request, self.template_name, {
            'doctor_user': doctor_user,
            'appointments_with_records': appointments_with_records,
        })

# Assign to keep the original function name
doctor_dashboard = DoctorDashboardView.as_view()



class RecordListView(View):
    template_name = 'patients/med-records.html'

    def get(self, request):
        # Handle GET request (to display the records)
        appointment_id = request.session.get('appointment_id')
        patient_id = request.session.get('patient_id')
        doctor_id = request.session.get('doctor_id')

        # Fetch medical records for the specific appointment
        records = MedicalRecord.objects.filter(appointment_id=appointment_id)
        recordform = CreateRecordForm()

        # Prepare the record list dictionary
        record_lists = {
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'records': records
        }

        # Render the template with the data
        return render(request, self.template_name, {
            'record_list': record_lists,
            'record_form': recordform,
        })

    def post(self, request):
        # Handle POST request (for updating or processing the record)
        appointment_id = request.POST.get('appointment_id') or request.session.get('appointment_id')
        patient_id = request.POST.get('patient_id') or request.session.get('patient_id')
        doctor_id = request.POST.get('doctor_id') or request.session.get('doctor_id')

        # Fetch medical records for the specific appointment
        records = MedicalRecord.objects.filter(appointment_id=appointment_id)
        recordform = CreateRecordForm(request.POST)

        if recordform.is_valid():
            # Use a transaction to ensure atomicity
            with transaction.atomic():
                # Save the record (if the form is valid)
                recordform.save()

                # You may also want to handle other related operations here if needed
                # For example: update related models or log the operation
                
                # Example: Assuming you have a method to log records
                # log_record_creation(recordform.instance)

        # Prepare the record list dictionary
        record_lists = {
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'records': records
        }

        # Render the template with the data
        return render(request, self.template_name, {
            'record_list': record_lists,
            'record_form': recordform,
        })

# Keep the original function name
record_list = RecordListView.as_view()






class RecordsView(View):
    template_name = 'patients/med-records.html'
    form_class = CreateRecordForm

    def post(self, request):
        # Handle POST request (form submission)
        records_form = self.form_class(request.POST)
        
        if records_form.is_valid():
            appointment_id = request.POST.get('appointment_id')
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
            type_edit = request.POST.get('type')

            # Debugging prints
            print(appointment_id)
            print(patient_id)
            print(doctor_id)
            print(type_edit)

            # Fetch related objects
            try:
                appointment = Appointment.objects.get(id=appointment_id)
                doctor = CustomUser.objects.get(id=doctor_id)
                patient = CustomUser.objects.get(id=patient_id)

                # Create or update the MedicalRecord based on the form data
                if type_edit == 'create':
                    MedicalRecord.objects.create(
                        diagnosis=records_form.cleaned_data['diagnosis'],
                        treatment=records_form.cleaned_data['treatment'],
                        notes=records_form.cleaned_data['notes'],
                        report=records_form.cleaned_data['report'],
                        appointment=appointment,
                        patient=patient,
                        doctor=doctor
                    )
                elif type_edit == 'update':
                    MedicalRecord.objects.filter(appointment=appointment).update(
                        diagnosis=records_form.cleaned_data['diagnosis'],
                        treatment=records_form.cleaned_data['treatment'],
                        notes=records_form.cleaned_data['notes'],
                        report=records_form.cleaned_data['report'],
                    )

                # Store IDs in session for later use
                request.session['appointment_id'] = appointment_id
                request.session['patient_id'] = patient_id
                request.session['doctor_id'] = doctor_id

                # Redirect to the record list page
                return redirect('record_list')
            except Exception as e:
                print("Error:", e)

        # If not valid, re-render the page with the form
        return render(request, self.template_name, {'form': records_form})

    def get(self, request):
        # Handle GET request (if needed to render form or show data initially)
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

# Assigning the view to the original function name
records = RecordsView.as_view()





class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'accounts/admin.html'

    # Check if the user is an admin
    def test_func(self):
        return self.request.user.is_admin()

    # Redirect non-admin users to the login page
    def handle_no_permission(self):
        return redirect('login')

    # Pass the required context data (doctors, patients, appointments, records)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['doctors'] = CustomUser.objects.filter(role='doctor')
        context['patients'] = CustomUser.objects.filter(role='patient')
        context['appointments'] = Appointment.objects.all()
        context['records'] = MedicalRecord.objects.all()
        return context

# Assign the view to the original function name
admin_dashboard = AdminDashboardView.as_view()


class AdminRequiredMixin(UserPassesTestMixin):
    """Mixin to check if the user is an admin."""

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin()

    def handle_no_permission(self):
        return redirect('login')

# Keep the original function name
admin_required = AdminRequiredMixin


class CustomLogoutView(LoginRequiredMixin, LogoutView):
    def get(self, request, *args, **kwargs):
        print("Logging out...")
        logout(request)
        return redirect('login')

    

# Assign the view to the original function name
user_logout = CustomLogoutView.as_view()


class DoctorListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'accounts/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 10  # Optional: if you want pagination

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

# Assign the view to the original function name
doctor_list_view = DoctorListView.as_view()


class DoctorDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'accounts/doctor_detail.html'
    context_object_name = 'doctor'

    def get_object(self):
        # Override to include role check
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='doctor')

# Assign the view to the original function name
doctor_detail_view = DoctorDetailView.as_view()


class CreateUpdateDoctorView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = CustomUser
    form_class = DoctorProfileForm
    template_name = 'accounts/doctor_form.html'
    context_object_name = 'doctor'

    def get_object(self, queryset=None):
        """Retrieve the doctor object for updating."""
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(CustomUser, pk=pk, role='doctor')
        return None  # For creating a new doctor

    def form_valid(self, form):
        """Handle form submission for creating or updating a doctor."""
        doctor_profile = form.save(commit=False)
        doctor_profile.role = 'doctor'  # Ensure role is set to 'doctor'
        doctor_profile.user = self.request.user  # Associate the doctor with the logged-in user
        doctor_profile.save()
        return redirect('doctor_list_view')

# Assign the view to the original function name
create_update_doctor_view = CreateUpdateDoctorView.as_view()


class DeleteDoctorView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'accounts/doctor_confirm_delete.html'
    context_object_name = 'doctor'
    success_url = reverse_lazy('doctor_list_view')  # Redirect to the doctor list after deletion

    def get_object(self, queryset=None):
        """Retrieve the doctor object to delete."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='doctor')

# Assign the view to the original function name
delete_doctor_view = DeleteDoctorView.as_view()



class PatientListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    
    def get_queryset(self):
        """Override to filter patients based on search query and gender filter."""
        search_query = self.request.GET.get('search', '')
        gender_filter = self.request.GET.get('gender', '')

        queryset = CustomUser.objects.filter(role='patient')

        if search_query:
            queryset = queryset.filter(full_name__icontains=search_query)

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

# Assign the view to the original function name
patient_list_view = PatientListView.as_view()


class PatientDetailView(LoginRequiredMixin, AdminRequiredMixin, DetailView):
    model = CustomUser
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'
    
    def get_object(self):
        """Override to get the patient object by primary key."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='patient')

# Assign the view to the original function name
patient_detail_view = PatientDetailView.as_view()

class CreateUpdatePatientView(LoginRequiredMixin, AdminRequiredMixin, CreateView, UpdateView):
    model = CustomUser
    form_class = PatientProfileForm
    template_name = 'patients/patient_form.html'
    success_url = reverse_lazy('patient_list_view')  # Redirect to patient list view

    def get_object(self, queryset=None):
        """Get the patient object based on the primary key."""
        pk = self.kwargs.get('pk')
        if pk:
            return get_object_or_404(CustomUser, pk=pk, role='patient')
        return None

    def form_valid(self, form):
        """Handle the valid form submission."""
        patient_profile = form.save(commit=False)
        patient_profile.role = 'patient'
        patient_profile.user = self.request.user
        patient_profile.save()
        return super().form_valid(form)

# Assign the view to the original function name
create_update_patient_view = CreateUpdatePatientView.as_view()


class DeletePatientView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list_view')  # Redirect to patient list view

    def get_object(self, queryset=None):
        """Get the patient object based on the primary key."""
        pk = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=pk, role='patient')

# Assign the view to the original function name
delete_patient_view = DeletePatientView.as_view()
