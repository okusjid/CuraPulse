from django.contrib import admin
from .models import CustomUser, Appointment, MedicalRecord  
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'role',  'created_at', 'updated_at')
    search_fields = ('full_name', 'email', 'role', 'specialization')
    list_filter = ('role', 'specialization', 'gender')
    ordering = ('full_name',)
    
    # Exclude groups and permissions from the form
    exclude = ('groups', 'user_permissions')

    # Organize fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('full_name', 'email', 'phone_number', 'gender', 'date_of_birth')
        }),
        ('Account Information', {
            'fields': ('username', 'password', 'role', 'specialization')
        }),
        ('Status and Timestamps', {
            'fields': ('is_active', 'is_staff', 'date_joined')
        }),
    )
    
    # To hash the password before saving it
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password'):
            obj.password = make_password(form.cleaned_data['password'])  # Ensure the password is hashed
        if not obj.pk:  
            obj.user = request.user  # Assuming the user field is related to who created the user
        super().save_model(request, obj, form, change)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'scheduled_at', 'created_at', 'status')
    search_fields = ('doctor__full_name', 'patient__full_name')
    list_filter = ('scheduled_at', 'doctor', 'patient')

    fieldsets = (
        ('Appointment Information', {
            'fields': ('doctor', 'patient', 'scheduled_at', 'status')
        })
        ,
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filter the queryset for doctors and patients
        form.base_fields['doctor'].queryset = CustomUser.objects.filter(role='doctor')
        form.base_fields['patient'].queryset = CustomUser.objects.filter(role='patient')
        return form

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'appointment', 'diagnosis', 'created_at', 'updated_at')
    search_fields = ('doctor__full_name', 'patient__full_name', 'diagnosis')
    
    list_filter = ('created_at', 'doctor', 'patient')

    fieldsets = (
        ('Appointment Information', {
            'fields': ('doctor', 'patient', 'appointment')
        }),
        ('Medical Details', {
            'fields': ('diagnosis', 'treatment', 'notes', 'report')
        }),
    )   

    # Make 'created_at' read-only
    readonly_fields = ('created_at',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Filter the queryset for doctors and patients
        form.base_fields['doctor'].queryset = CustomUser.objects.filter(role='doctor')
        form.base_fields['patient'].queryset = CustomUser.objects.filter(role='patient')
        return form

    # Optional: If you need to handle saving reports or diagnosis validation
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user  # Assuming you track who created the record
        super().save_model(request, obj, form, change)


admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MedicalRecord, MedicalRecordAdmin)

try:
    admin.site.unregister(Group)
    admin.site.unregister(Permission)
except admin.sites.NotRegistered:
    pass
