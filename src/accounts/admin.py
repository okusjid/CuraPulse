from django.contrib import admin
from .models import CustomUser, Appointment, MedicalRecord  
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'role', 'created_at')
    search_fields = ('full_name', 'email', 'role', 'specialization')
    list_filter = ('role', 'specialization', 'gender')
    ordering = ('full_name',)
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:  
            obj.user = request.user  
            
        super().save_model(request, obj, form, change)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'scheduled_at', 'created_at')
    search_fields = ('doctor__full_name', 'patient__full_name')
    list_filter = ('scheduled_at', 'doctor', 'patient')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['doctor'].queryset = CustomUser.objects.filter(role='doctor')
        form.base_fields['patient'].queryset = CustomUser.objects.filter(role='patient')
        return form

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MedicalRecord)

