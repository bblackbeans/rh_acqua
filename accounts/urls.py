from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Candidate Profile
    path('perfil/', views.profile_view, name='profile_view'),
    path('perfil/editar/', views.profile_edit, name='profile_edit'),

    # Applications
    path('minhas-candidaturas/', views.my_applications, name='my_applications'),

    # Add URLs for registration, login, logout if not using django.contrib.auth.urls
    # Example using django.contrib.auth:
    # path('', include('django.contrib.auth.urls')),
]

