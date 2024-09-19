from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from ..models import MedicalRecord, Appointment, CustomUser
from ..forms import CreateRecordForm
import logging
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

logger = logging.getLogger(__name__)

class RecordListView(LoginRequiredMixin, View):
    """
    A view to display and manage medical records associated with an appointment, patient, and doctor.
    Caches the medical records for faster access and invalidates the cache when a new record is added.
    """

    template_name = 'patients/med-records.html'

    def get(self, request):
        """
        Handles the GET request to display medical records for a specific appointment, patient, and doctor.
        Uses caching to improve performance.
        """
        appointment_id = request.session.get('appointment_id')
        patient_id = request.session.get('patient_id')
        doctor_id = request.session.get('doctor_id')

        # Cache key based on the appointment, patient, and doctor IDs
        cache_key = f'record_list_{appointment_id}_{patient_id}_{doctor_id}'
        records = cache.get(cache_key)

        if records is None:
            logger.info(f'Cache miss for key: {cache_key}')
            records = MedicalRecord.objects.filter(appointment_id=appointment_id)
            cache.set(cache_key, records, timeout=60)
        else:
            logger.info(f'Cache hit for key: {cache_key}')

        record_form = CreateRecordForm()

        record_lists = {
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'records': records
        }

        return render(request, self.template_name, {
            'record_list': record_lists,
            'record_form': record_form,
        })

    def post(self, request):
        """
        Handles the POST request to create a new medical record and invalidates the relevant cache entry.
        """
        appointment_id = request.POST.get('appointment_id') or request.session.get('appointment_id')
        patient_id = request.POST.get('patient_id') or request.session.get('patient_id')
        doctor_id = request.POST.get('doctor_id') or request.session.get('doctor_id')

        records = MedicalRecord.objects.filter(appointment_id=appointment_id)
        record_form = CreateRecordForm(request.POST)

        if record_form.is_valid():
            try:
                with transaction.atomic():
                    record_form.save()

                cache_key = f'record_list_{appointment_id}_{patient_id}_{doctor_id}'
                cache.delete(cache_key)
                logger.info(f'Cache invalidated for key: {cache_key}')

                return redirect('record_list_view')  # Redirect after successful creation
            except Exception as e:
                logger.error(f"Error saving record: {e}")
                record_form.add_error(None, "There was an error saving the record.")

        record_lists = {
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'doctor_id': doctor_id,
            'records': records
        }

        return render(request, self.template_name, {
            'record_list': record_lists,
            'record_form': record_form,
        })

# Use this view in your URLs
record_list_view = RecordListView.as_view()


class RecordsView(LoginRequiredMixin, View):
    """
    A view to handle the creation and updating of medical records for a specific appointment, patient, and doctor.
    """

    template_name = 'patients/med-records.html'
    form_class = CreateRecordForm

    def get(self, request):
        """
        Handles the GET request to render a form for either creating or updating a medical record.
        The form will be pre-filled if updating a record.
        """
        appointment_id = request.GET.get('appointment_id')
        patient_id = request.GET.get('patient_id')
        doctor_id = request.GET.get('doctor_id')
        type_edit = request.GET.get('type')

        logger.info(f"Received: appointment_id={appointment_id}, patient_id={patient_id}, doctor_id={doctor_id}, type_edit={type_edit}")

        if type_edit == 'update':
            try:
                medical_record = MedicalRecord.objects.get(appointment_id=appointment_id, patient_id=patient_id)
                form = self.form_class(instance=medical_record)
            except MultipleObjectsReturned:
                medical_records = MedicalRecord.objects.filter(appointment_id=appointment_id, patient_id=patient_id)
                form = self.form_class(instance=medical_records.first())  # Using the first record (not ideal)
                logger.warning(f"Multiple medical records found for appointment_id={appointment_id} and patient_id={patient_id}")
            except MedicalRecord.DoesNotExist:
                logger.info(f"No record found for appointment_id={appointment_id}, patient_id={patient_id}")
                form = self.form_class()  # Show an empty form
        else:
            form = self.form_class()

        return render(request, self.template_name, {
            'form': form,
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'doctor_id': doctor_id
        })

    def post(self, request):
        """
        Handles the POST request to create or update a medical record. The form data is validated,
        and the record is either created or updated in the database.
        """
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
                logger.error(f"Error during record creation/updating: {e}")
                # Handle error, possibly show a message to the user
                records_form.add_error(None, "There was an error saving the medical record.")

        return render(request, self.template_name, {
            'form': records_form,
            'appointment_id': appointment_id,
            'patient_id': patient_id,
            'doctor_id': doctor_id
        })

# View instantiation
records_view = RecordsView.as_view()
