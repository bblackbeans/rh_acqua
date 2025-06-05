"""hr_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings # Required for static/media files in development
from django.conf.urls.static import static # Required for static/media files in development

# Import a basic view for the home page (to be created)
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vagas/", include("vacancies.urls", namespace="vacancies")),
    path("conta/", include("accounts.urls", namespace="accounts")),
    # Add other app URLs here (e.g., notifications)

    # Include Django's built-in auth URLs for login/logout etc.
    # path("conta/", include("django.contrib.auth.urls")), # Provides login, logout, password reset etc.

    # Home page
    path("", core_views.home, name="home"), # Define a home view in core app
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Add static files serving if needed and not handled by webserver
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

