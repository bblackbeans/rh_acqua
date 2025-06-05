from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import CandidateProfile, Education, ComplementaryCourse, WorkExperience

# Inlines for related models to show on CandidateProfile page
class EducationInline(admin.TabularInline):
    model = Education
    extra = 1 # Number of empty forms to display
    fields = (
        "level",
        "course",
        "institution",
        "status",
        "conclusion_year",
    )

class ComplementaryCourseInline(admin.TabularInline):
    model = ComplementaryCourse
    extra = 1
    fields = (
        "course_name",
        "institution",
        "duration_hours",
        "completion_year",
    )

class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 1
    fields = (
        "role",
        "company",
        "start_date",
        "end_date",
        "responsibilities",
    )
    # Use widgets for better date input if needed
    # formfield_overrides = {
    #     models.DateField: {"widget": admin.widgets.AdminDateWidget},
    # }

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "cpf", "phone_whatsapp", "address_city", "address_state", "updated_at")
    search_fields = ("full_name", "cpf", "user__username", "user__email", "address_city")
    list_filter = ("address_state", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    inlines = [EducationInline, ComplementaryCourseInline, WorkExperienceInline]
    fieldsets = (
        (None, {"fields": ("user", "full_name", "social_name", "birth_date")}),
        ("Documentos", {"fields": ("cpf", "rg", "rg_issue_date", "rg_issuer")}),
        ("Contato", {"fields": ("phone_whatsapp",)}),
        ("Endereço", {"fields": (
            "address_street", "address_number", "address_complement",
            "address_neighborhood", "address_city", "address_state", "address_zip"
        )}),
        ("Currículo", {"fields": ("cv_file",)}),
        ("Datas", {"fields": ("created_at", "updated_at")}),
    )
    # Use autocomplete_fields if User list becomes large
    # autocomplete_fields = ["user"]

# Optionally, integrate CandidateProfile into the User admin
# class CandidateProfileInline(admin.StackedInline):
#     model = CandidateProfile
#     can_delete = False
#     verbose_name_plural = "Perfil de Candidato"
#     fk_name = "user"
#     fields = ("full_name", "cpf", "phone_whatsapp") # Show only key fields

# class CustomUserAdmin(BaseUserAdmin):
#     inlines = (CandidateProfileInline,)
#     list_display = ("username", "email", "first_name", "last_name", "is_staff", "get_candidate_profile_link")
#     list_select_related = ("candidate_profile",)

#     def get_candidate_profile_link(self, instance):
#         # Add link to candidate profile if exists
#         pass # Implementation needed
#     get_candidate_profile_link.short_description = "Perfil Candidato"

#     def get_inline_instances(self, request, obj=None):
#         if not obj:
#             return list()
#         return super().get_inline_instances(request, obj)

# Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)

# Register other models if direct access is needed (usually managed via CandidateProfile inline)
# admin.site.register(Education)
# admin.site.register(ComplementaryCourse)
# admin.site.register(WorkExperience)

