"""
URL configuration for hospital_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import debug_toolbar
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Define the security scheme for Bearer token
schema_view = get_schema_view(
    openapi.Info(
        title="HealthSync API",
        default_version='v1',
        description="API documentation for HealthSync",
        contact=openapi.Contact(email="usjidn@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    # Security definition for Bearer token
    authentication_classes=[],  # Optional, if your API has specific authentication
)

# Security scheme for Bearer token
schema_view = get_schema_view(
    openapi.Info(
        title="HealthSync API",

         
        default_version='v1',
        description="API documentation for HealthSync",
        contact=openapi.Contact(email="usjidn@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Update the urlpatterns to include swagger with security settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("accounts.urls")),
    path('__debug__/', include(debug_toolbar.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
]

admin.site.site_header = "CuraPulse"
admin.site.site_title = "CuraPulse Admin Portal"    
admin.site.index_title = "CuraPulse Admin Portal"


