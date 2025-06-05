from django.contrib import admin
from .models import Notification, ActivityLog

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "message_summary", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("recipient__username", "message", "related_application__candidate__full_name", "related_vacancy__title")
    readonly_fields = ("created_at", "recipient", "related_application", "related_vacancy")
    autocomplete_fields = ["recipient", "related_application", "related_vacancy"]
    list_select_related = ("recipient",)

    def message_summary(self, obj):
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    message_summary.short_description = "Mensagem (resumo)"

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "actor_display", "verb", "target_summary")
    list_filter = ("verb", "timestamp")
    search_fields = ("actor__username", "verb", "details")
    readonly_fields = ("timestamp", "actor", "verb", "target_application", "target_vacancy", "target_candidate", "details")
    autocomplete_fields = ["actor", "target_application", "target_vacancy", "target_candidate"]
    list_select_related = ("actor", "target_application", "target_vacancy", "target_candidate")

    def actor_display(self, obj):
        return obj.actor.username if obj.actor else "Sistema"
    actor_display.short_description = "Ator"

    def target_summary(self, obj):
        if obj.target_application:
            return f"Candidatura: {obj.target_application}"
        elif obj.target_vacancy:
            return f"Vaga: {obj.target_vacancy}"
        elif obj.target_candidate:
            return f"Candidato: {obj.target_candidate}"
        return "N/A"
    target_summary.short_description = "Alvo"

