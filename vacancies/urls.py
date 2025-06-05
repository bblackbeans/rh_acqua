from django.urls import path
from . import views

app_name = 'vacancies'

urlpatterns = [
    # Candidate Views
    path('', views.vacancy_list, name='list'),
    path('vaga/<int:vacancy_id>/', views.vacancy_detail, name='detail'),
    path('vaga/<int:vacancy_id>/candidatar/', views.apply_for_vacancy, name='apply'),
    path('candidatura/sucesso/', views.application_success, name='application_success'),
    path('vaga/ja-aplicada/', lambda request: render(request, 'vacancies/already_applied.html'), name='already_applied'), # Simple static render or pass context

    # Recruiter Views
    path('recrutador/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('recrutador/vaga/<int:vacancy_id>/candidaturas/', views.recruiter_applications_list, name='recruiter_applications_list'),
    path('recrutador/candidatura/<int:application_id>/', views.recruiter_application_detail, name='recruiter_application_detail'),
    path('recrutador/candidatura/<int:application_id>/status/', views.recruiter_change_application_status, name='recruiter_change_application_status'),
    path('recrutador/candidatura/<int:application_id>/agendar-entrevista/', views.recruiter_schedule_interview, name='recruiter_schedule_interview'),

    # Note: my_applications might belong in the 'accounts' app urls
    # path('minhas-candidaturas/', views.my_applications, name='my_applications'), # Moved to accounts/urls.py
]

