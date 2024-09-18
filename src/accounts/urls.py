from django.urls import path
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from . import views
from rest_framework.authtoken.views import obtain_auth_token
from accounts.views.appointments_views import AppointmentListCreateAPIView , AppointmentDetailAPIView
from django.urls import path
urlpatterns = [
    # User URL:
    path('', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page=''), name='logout'),

    # Doctor URL:
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor-dashboard/<int:doctor_id>/', views.doctor_dashboard, name='doctor_dashboard_with_id'),
    path('doctors/', views.doctor_list_view, name='doctor_list_view'),
    path('doctors/<int:pk>/', views.doctor_detail_view, name='doctor_detail_view'),
    path('doctors/create/', views.create_update_doctor_view, name='create_doctor_view'),
    path('doctors/update/<int:pk>/', views.create_update_doctor_view, name='update_doctor_view'),
    path('doctors/delete/<int:pk>/', views.delete_doctor_view, name='delete_doctor_view'),

    # Record URL:
    path('record/', views.records_view, name='records'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('reports/appointments/', views.admin_appointment_report_view, name='admin_appointment_report_view'),

    # Patient URL:
    path('patients/', views.patient_list_view, name='patient_list_view'),
    path('patients/<int:pk>/', views.patient_detail_view, name='patient_detail_view'),
    path('patients/create/', views.create_update_patient_view, name='create_patient_view'),
    path('patients/update/<int:pk>/', views.create_update_patient_view, name='update_patient_view'),
    path('patients/delete/<int:pk>/', views.delete_patient_view, name='delete_patient_view'),
    path('patient-medical-records/', views.record_list_view, name='record_list'),

    # Appointment URLs:
    path('appointments/', AppointmentListCreateAPIView.as_view(), name='appointment-list-create'),
    path('appointments/<int:pk>/', AppointmentDetailAPIView.as_view(), name='appointment-detail'),

    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),


 
  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





