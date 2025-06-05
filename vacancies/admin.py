from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
import json
from .vendor.jsoneditor.forms import JSONEditorWidget
from .models import JobVacancyType, JobVacancy, JobApplication, Interview

# Define a basic schema for field_config validation (can be expanded)
FIELD_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "personal_data": {"type": "object"},
        "professional_council": {"type": "object"},
        "pcd_details": {"type": "object"},
        "education": {"type": "object"},
        "complementary_courses": {"type": "object"},
        "work_experience": {"type": "object"},
        "specific_questions": {"type": "array", "items": {"type": "object"}},
        "emotional_skills": {"type": "object"},
        "availability": {"type": "object"},
        "relatives": {"type": "object"}
    }
}

class JobVacancyTypeAdminForm(forms.ModelForm):
    class Meta:
        model = JobVacancyType
        fields = "__all__"
        widgets = {
            "field_config": JSONEditorWidget(schema=FIELD_CONFIG_SCHEMA, collapsed=False),
        }

    def clean_field_config(self):
        config = self.cleaned_data.get("field_config")
        if isinstance(config, str): # Sometimes widget might return string
            try:
                config = json.loads(config)
            except json.JSONDecodeError:
                raise ValidationError("Formato JSON inválido.")
        # Add more specific validation based on the schema or rules if needed
        # Example: Check if required keys exist within sections
        # if "personal_data" in config and "cpf" not in config["personal_data"]:
        #     raise ValidationError("A seção 'personal_data' deve conter a chave 'cpf'.")
        return config

@admin.register(JobVacancyType)
class JobVacancyTypeAdmin(admin.ModelAdmin):
    form = JobVacancyTypeAdminForm
    list_display = ("name", "description")
    search_fields = ("name",)

class InterviewInline(admin.TabularInline):
    model = Interview
    extra = 0 # Don't show empty forms by default
    fields = ("scheduled_time", "interviewer", "interview_type", "status", "location_details")
    readonly_fields = ("application",)
    autocomplete_fields = ["interviewer"]
    ordering = ("scheduled_time",)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job_vacancy", "status", "application_date", "score")
    list_filter = ("status", "job_vacancy__hospital_unit", "job_vacancy__vacancy_type", "application_date")
    search_fields = ("candidate__full_name", "candidate__cpf", "job_vacancy__title")
    readonly_fields = ("application_date", "candidate", "job_vacancy", "submitted_data", "pcd_medical_report_file") # Make submitted data read-only here
    autocomplete_fields = ["candidate", "job_vacancy"]
    inlines = [InterviewInline]
    fieldsets = (
        ("Informações da Candidatura", {"fields": ("candidate", "job_vacancy", "application_date", "status", "score")}),
        ("Dados Submetidos", {"fields": ("submitted_data", "pcd_medical_report_file")}), # Consider a custom widget for better display
        ("Notas Internas", {"fields": ("recruiter_notes",)}),
    )

@admin.register(JobVacancy)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "hospital_unit", "vacancy_type", "status", "created_at")
    list_filter = ("status", "hospital_unit__state", "hospital_unit", "vacancy_type", "created_at")
    search_fields = ("title", "description", "requirements", "hospital_unit__name", "vacancy_type__name")
    readonly_fields = ("created_at", "updated_at", "created_by")
    autocomplete_fields = ["hospital_unit", "department", "vacancy_type", "created_by"]
    fieldsets = (
        (None, {"fields": ("title", "vacancy_type", "status")}),
        ("Localização", {"fields": ("hospital_unit", "department")}),
        ("Detalhes da Vaga", {"fields": ("description", "requirements", "salary_range")}),
        ("Metadados", {"fields": ("created_by", "created_at", "updated_at")}),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk: # Set created_by only on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Interview admin is usually managed via JobApplication inline, but register if direct access is needed
# @admin.register(Interview)
# class InterviewAdmin(admin.ModelAdmin):
#     list_display = ("application", "interviewer", "scheduled_time", "status")
#     list_filter = ("status", "interview_type", "scheduled_time")
#     search_fields = ("application__candidate__full_name", "interviewer__username")
#     autocomplete_fields = ["application", "interviewer"]

