from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction  # Import transaction
from ..models import MedicalRecord, Appointment, CustomUser
from ..forms import CreateRecordForm

from django.core.cache import cache


# Record List View (Admin only)
class RecordListView(LoginRequiredMixin, View):
    template_name = 'patients/med-records.html'

    def get(self, request):
        # Retrieve appointment, patient, and doctor from session (or URL parameters)
        appointment_id = request.session.get('appointment_id')
        patient_id = request.session.get('patient_id')
        doctor_id = request.session.get('doctor_id')

        # Create a unique cache key for this specific record list
        cache_key = f'record_list_{appointment_id}_{patient_id}_{doctor_id}'
        
        # Try to get the records from cache
        records = cache.get(cache_key)
        if records is None:
            # Cache miss: Fetch medical records for the specific appointment
            records = MedicalRecord.objects.filter(appointment_id=appointment_id)
            # Cache the result for 1 minute (for testing)
            cache.set(cache_key, records, timeout=60)  # 1 minute timeout for testing

        # Create an empty form for adding new records
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

            # Invalidate the cache when new data is saved
            cache_key = f'record_list_{appointment_id}_{patient_id}_{doctor_id}'
            cache.delete(cache_key)  # Clear the cache so it will be refreshed on the next GET request

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


from django.core.exceptions import MultipleObjectsReturned

class RecordsView(LoginRequiredMixin, View):
    template_name = 'patients/med-records.html'
    form_class = CreateRecordForm

    def get(self, request):
        appointment_id = request.GET.get('appointment_id')
        patient_id = request.GET.get('patient_id')
        doctor_id = request.GET.get('doctor_id')
        type_edit = request.GET.get('type')

        print(f"Received: appointment_id={appointment_id}, patient_id={patient_id}, doctor_id={doctor_id}, type_edit={type_edit}")

        if type_edit == 'update':
            try:
                medical_record = MedicalRecord.objects.get(appointment_id=appointment_id, patient_id=patient_id)
                form = self.form_class(instance=medical_record)
            except MultipleObjectsReturned:
                medical_records = MedicalRecord.objects.filter(appointment_id=appointment_id, patient_id=patient_id)
                form = self.form_class(instance=medical_records.first())  # Using the first record (not ideal)
            except MedicalRecord.DoesNotExist:
                print(f"No record found for appointment_id={appointment_id}, patient_id={patient_id}")
                form = self.form_class()  # Show an empty form
        else:
            form = self.form_class()

        return render(request, self.template_name, {'form': form, 'appointment_id': appointment_id, 'patient_id': patient_id, 'doctor_id': doctor_id})

    def post(self, request):
        records_form = self.form_class(request.POST, request.FILES)  # Include request.FILES to handle file uploads

        if records_form.is_valid():
            appointment_id = request.POST.get('appointment_id')
            patient_id = request.POST.get('patient_id')
            doctor_id = request.POST.get('doctor_id')
            type_edit = request.POST.get('type')

            try:
                with transaction.atomic():
                    appointment = Appointment.objects.get(id=appointment_id)
                    doctor = CustomUser.objects.get(id=doctor_id)
                    patient = CustomUser.objects.get(id=patient_id)

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
                        # Update the existing record
                        medical_record = MedicalRecord.objects.get(appointment=appointment, patient=patient)
                        for field, value in records_form.cleaned_data.items():
                            setattr(medical_record, field, value)
                        medical_record.save()

                    request.session['appointment_id'] = appointment_id
                    request.session['patient_id'] = patient_id
                    request.session['doctor_id'] = doctor_id

                return redirect('record_list_view')  # Redirect to your list view after the update

            except Exception as e:
                print("Error:", e)
                # Handle error, possibly show a message to the user

        return render(request, self.template_name, {'form': records_form, 'appointment_id': appointment_id, 'patient_id': patient_id, 'doctor_id': doctor_id})

# View instantiation
records_view = RecordsView.as_view()
