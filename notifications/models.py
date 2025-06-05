from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from vacancies.models import JobApplication, JobVacancy # Import related models
from accounts.models import CandidateProfile

class Notification(models.Model):
    class NotificationTypeChoices(models.TextChoices):
        STATUS_UPDATE = 'STATUS_UPDATE', _('Atualização de Status')
        INTERVIEW_SCHEDULED = 'INTERVIEW_SCHEDULED', _('Entrevista Agendada')
        NEW_VACANCY = 'NEW_VACANCY', _('Nova Vaga Correspondente')
        APPLICATION_RECEIVED = 'APPLICATION_RECEIVED', _('Candidatura Recebida')
        GENERAL = 'GENERAL', _('Geral')

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name=_("Destinatário"))
    message = models.TextField(_("Mensagem"))
    notification_type = models.CharField(_("Tipo de Notificação"), max_length=30, choices=NotificationTypeChoices.choices, default=NotificationTypeChoices.GENERAL)
    related_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, blank=True, null=True, related_name='notifications', verbose_name=_("Candidatura Relacionada"))
    related_vacancy = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, blank=True, null=True, related_name='notifications', verbose_name=_("Vaga Relacionada"))
    is_read = models.BooleanField(_("Lida"), default=False)
    created_at = models.DateTimeField(_("Criada em"), auto_now_add=True)

    def __str__(self):
        return f"Notificação para {self.recipient.username} - {self.get_notification_type_display()}"

    class Meta:
        verbose_name = _("Notificação")
        verbose_name_plural = _("Notificações")
        ordering = ["-created_at"]

class ActivityLog(models.Model):
    # Actor can be null for system-generated actions
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='actions', verbose_name=_("Ator"))
    verb = models.CharField(_("Ação"), max_length=255, help_text=_("Ex: candidatou-se, atualizou_status, agendou_entrevista, criou_vaga"))
    # Using GenericForeignKey could be an alternative, but explicit FKs are simpler here
    target_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, blank=True, null=True, related_name='activity_logs', verbose_name=_("Candidatura Alvo"))
    target_vacancy = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, blank=True, null=True, related_name='activity_logs', verbose_name=_("Vaga Alvo"))
    target_candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, blank=True, null=True, related_name='activity_logs', verbose_name=_("Candidato Alvo"))
    details = models.JSONField(_("Detalhes Adicionais"), blank=True, null=True, help_text=_("Ex: status antigo/novo, detalhes da entrevista"))
    timestamp = models.DateTimeField(_("Data/Hora"), auto_now_add=True)

    def __str__(self):
        actor_name = self.actor.username if self.actor else "Sistema"
        return f"{actor_name} {self.verb} em {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        verbose_name = _("Registro de Atividade")
        verbose_name_plural = _("Registros de Atividade")
        ordering = ["-timestamp"]

