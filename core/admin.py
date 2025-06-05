from django.contrib import admin
from .models import HospitalUnit, Department

@admin.register(HospitalUnit)
class HospitalUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "state")
    search_fields = ("name", "city", "state")
    list_filter = ("state", "city")

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "hospital_unit")
    search_fields = ("name", "hospital_unit__name")
    list_filter = ("hospital_unit__state", "hospital_unit")
    autocomplete_fields = ["hospital_unit"]

