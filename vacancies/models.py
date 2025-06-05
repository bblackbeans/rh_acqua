from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from core.models import HospitalUnit, Department # Import related models from core app
from accounts.models import CandidateProfile # Import CandidateProfile

class JobVacancyType(models.Model):
    name = models.CharField(_("Nome do Tipo de Vaga"), max_length=255, unique=True)
    description = models.TextField(_("Descrição"), blank=True, null=True)
    # field_config stores the dynamic form structure for this vacancy type
    field_config = models.JSONField(_("Configuração de Campos do Formulário"), default=dict, help_text=_("Estrutura JSON definindo os campos e suas propriedades (visibilidade, obrigatoriedade, etc.) para este tipo de vaga."))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tipo de Vaga")
        verbose_name_plural = _("Tipos de Vaga")
        ordering = ["name"]

class JobVacancy(models.Model):
    class StatusChoices(models.TextChoices):
        OPEN = 'OPEN', _('Aberta')
        CLOSED = 'CLOSED', _('Fechada')
        FILLED = 'FILLED', _('Preenchida')

    title = models.CharField(_("Título da Vaga"), max_length=255)
    description = models.TextField(_("Descrição Detalhada"))
    requirements = models.TextField(_("Requisitos"))
    salary_range = models.CharField(_("Faixa Salarial"), max_length=100, blank=True, null=True)
    hospital_unit = models.ForeignKey(HospitalUnit, on_delete=models.PROTECT, related_name='vacancies', verbose_name=_("Unidade Hospitalar"))
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, related_name='vacancies', blank=True, null=True, verbose_name=_("Setor"))
    vacancy_type = models.ForeignKey(JobVacancyType, on_delete=models.PROTECT, related_name='vacancies', verbose_name=_("Tipo de Vaga"))
    status = models.CharField(_("Status"), max_length=10, choices=StatusChoices.choices, default=StatusChoices.OPEN)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_vacancies', null=True, verbose_name=_("Criado por"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.hospital_unit.name})"

    class Meta:
        verbose_name = _("Vaga")
        verbose_name_plural = _("Vagas")
        ordering = ["-created_at"]

class JobApplication(models.Model):
    class StatusChoices(models.TextChoices):
        RECEIVED = 'RECEIVED', _('Recebida')
        SCREENING = 'SCREENING', _('Triagem')
        INTERVIEW = 'INTERVIEW', _('Entrevista')
        TEST = 'TEST', _('Teste')
        OFFER = 'OFFER', _('Oferta')
        HIRED = 'HIRED', _('Contratado')
        REJECTED = 'REJECTED', _('Rejeitado')
        CANCELED = 'CANCELED', _('Cancelada') # Candidate withdrew

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications', verbose_name=_("Candidato"))
    job_vacancy = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, related_name='applications', verbose_name=_("Vaga"))
    application_date = models.DateTimeField(_("Data da Candidatura"), auto_now_add=True)
    status = models.CharField(_("Status da Candidatura"), max_length=15, choices=StatusChoices.choices, default=StatusChoices.RECEIVED)
    score = models.FloatField(_("Score (Triagem)"), blank=True, null=True)
    recruiter_notes = models.TextField(_("Notas do Recrutador"), blank=True, null=True)
    # submitted_data stores the candidate's answers based on vacancy_type.field_config
    submitted_data = models.JSONField(_("Dados Submetidos na Candidatura"), default=dict)
    pcd_medical_report_file = models.FileField(_("Laudo Médico PCD"), upload_to='laudos/', blank=True, null=True)

    def __str__(self):
        return f"Candidatura de {self.candidate.full_name} para {self.job_vacancy.title}"

    class Meta:
        verbose_name = _("Candidatura")
        verbose_name_plural = _("Candidaturas")
        ordering = ["-application_date"]
        unique_together = [("candidate", "job_vacancy")] # Candidate can apply only once per vacancy

class Interview(models.Model):
    class StatusChoices(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Agendada')
        COMPLETED = 'COMPLETED', _('Realizada')
        CANCELED = 'CANCELED', _('Cancelada')
        RESCHEDULED = 'RESCHEDULED', _('Reagendada')
        NO_SHOW = 'NO_SHOW', _('Não Compareceu')

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews', verbose_name=_("Candidatura"))
    interviewer = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='conducted_interviews', null=True, verbose_name=_("Entrevistador"))
    scheduled_time = models.DateTimeField(_("Data/Hora Agendada"))
    interview_type = models.CharField(_("Tipo de Entrevista"), max_length=100, blank=True, null=True, help_text=_("Ex: Triagem RH, Técnica, Gestor"))
    location_details = models.TextField(_("Detalhes/Localização"), blank=True, null=True, help_text=_("Ex: Link da videochamada, Sala X"))
    status = models.CharField(_("Status"), max_length=15, choices=StatusChoices.choices, default=StatusChoices.SCHEDULED)
    recruiter_feedback = models.TextField(_("Feedback do Entrevistador"), blank=True, null=True)
    candidate_feedback = models.TextField(_("Feedback do Candidato"), blank=True, null=True) # Optional field for candidate input

    def __str__(self):
        return f"Entrevista para {self.application.candidate.full_name} - {self.get_status_display()}"

    class Meta:
        verbose_name = _("Entrevista")
        verbose_name_plural = _("Entrevistas")
        ordering = ["scheduled_time"]

