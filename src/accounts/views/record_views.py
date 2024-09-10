from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction  # Import transaction
from ..models import MedicalRecord, Appointment, CustomUser
from ..forms import CreateRecordForm

# Record List View (for a specific appointment)
class RecordListView(LoginRequiredMixin, View):
    template_name = 'patients/med-records.html'

    def get(self, request):
        # Retrieve appointment, patient, and doctor from session (or URL parameters)
        appointment_id = request.session.get('appointment_id')
        patient_id = request.session.get('patient_id')
        doctor_id = request.session.get('doctor_id')

        # Fetch medical records for the specific appointment
        records = MedicalRecord.objects.filter(appointment_id=appointment_id)
        record_form = CreateRecordForm()

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
            'record_form': record_form,
        })

    def post(self, request):
        # Handle POST request (form submission for creating or updating records)
        appointment_id = request.POST.get('appointment_id') or request.session.get('appointment_id')
        patient_id = request.POST.get('patient_id') or request.session.get('patient_id')
        doctor_id = request.POST.get('doctor_id') or request.session.get('doctor_id')

        # Fetch medical records for the specific appointment
        records = MedicalRecord.objects.filter(appointment_id=appointment_id)
        record_form = CreateRecordForm(request.POST)

        if record_form.is_valid():
            # Use transaction to ensure atomicity
            with transaction.atomic():
                # Save or update the record (if the form is valid)
                record_form.save()

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
            'record_form': record_form,
        })

record_list_view = RecordListView.as_view()

# Create or Update Medical Records View
class RecordsView(LoginRequiredMixin, View):
    template_name = 'patients/med-records.html'
    form_class = CreateRecordForm

    def get(self, request):
        # Render the form for creating or updating records
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        # Handle POST request for form submission (create or update a record)
        records_form = self.form_class(request.POST)

        if records_form.is_valid():
            appointment_id = request.POST.get('appointment_id')
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
            type_edit = request.POST.get('type')

            # Use transaction to ensure atomicity
            try:
                with transaction.atomic():
                    # Fetch related objects
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
                return redirect('record_list_view')
            except Exception as e:
                print("Error:", e)

        # If not valid, re-render the page with the form
        return render(request, self.template_name, {'form': records_form})

records_view = RecordsView.as_view()
