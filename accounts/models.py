from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Choices for address state (Brazilian UFs)
UF_CHOICES = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins")
]

# Choices for Education Level
EDUCATION_LEVEL_CHOICES = [
    ("FUND_INC", _("Ensino Fundamental Incompleto")),
    ("FUND_COMP", _("Ensino Fundamental Completo")),
    ("MED_INC", _("Ensino Médio Incompleto")),
    ("MED_COMP", _("Ensino Médio Completo")),
    ("SUP_INC", _("Superior Incompleto")),
    ("SUP_COMP", _("Superior Completo")),
    ("POS", _("Pós-graduação")),
    ("MEST", _("Mestrado")),
    ("DOUT", _("Doutorado")),
]

# Choices for Education Status
EDUCATION_STATUS_CHOICES = [
    ("COMPLETO", _("Completo")),
    ("CURSANDO", _("Cursando")),
    ("INCOMPLETO", _("Incompleto")),
]

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    full_name = models.CharField(_("Nome Completo"), max_length=255)
    social_name = models.CharField(_("Nome Social"), max_length=255, blank=True, null=True)
    birth_date = models.DateField(_("Data de Nascimento"))
    cpf = models.CharField(_("CPF"), max_length=14, unique=True) # Masked format XXX.XXX.XXX-XX
    rg = models.CharField(_("RG"), max_length=20)
    rg_issue_date = models.DateField(_("Data de Emissão RG"), blank=True, null=True)
    rg_issuer = models.CharField(_("Órgão Emissor RG"), max_length=50, blank=True, null=True)
    phone_whatsapp = models.CharField(_("Telefone com WhatsApp"), max_length=20)
    address_street = models.CharField(_("Rua"), max_length=255)
    address_number = models.CharField(_("Número"), max_length=20)
    address_complement = models.CharField(_("Complemento"), max_length=100, blank=True, null=True)
    address_neighborhood = models.CharField(_("Bairro"), max_length=100)
    address_city = models.CharField(_("Cidade"), max_length=100)
    address_state = models.CharField(_("Estado"), max_length=2, choices=UF_CHOICES)
    address_zip = models.CharField(_("CEP"), max_length=9) # Masked format XXXXX-XXX
    cv_file = models.FileField(_("Currículo (CV)"), upload_to='cvs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _("Perfil do Candidato")
        verbose_name_plural = _("Perfis dos Candidatos")

class Education(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='education_history')
    level = models.CharField(_("Nível de Escolaridade"), max_length=10, choices=EDUCATION_LEVEL_CHOICES)
    course = models.CharField(_("Curso"), max_length=255, blank=True, null=True)
    institution = models.CharField(_("Instituição de Ensino"), max_length=255)
    conclusion_year = models.PositiveIntegerField(_("Ano de Conclusão"), blank=True, null=True)
    status = models.CharField(_("Status"), max_length=10, choices=EDUCATION_STATUS_CHOICES, default='COMPLETO')

    def __str__(self):
        return f"{self.get_level_display()} - {self.institution}"

    class Meta:
        verbose_name = _("Formação Acadêmica")
        verbose_name_plural = _("Formações Acadêmicas")
        ordering = ['-conclusion_year']

class ComplementaryCourse(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='complementary_courses')
    course_name = models.CharField(_("Nome do Curso"), max_length=255)
    institution = models.CharField(_("Instituição"), max_length=255)
    duration_hours = models.PositiveIntegerField(_("Carga Horária (horas)"), blank=True, null=True)
    completion_year = models.PositiveIntegerField(_("Ano de Realização"), blank=True, null=True)

    def __str__(self):
        return self.course_name

    class Meta:
        verbose_name = _("Curso Complementar")
        verbose_name_plural = _("Cursos Complementares")
        ordering = ['-completion_year']

class WorkExperience(models.Model):
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='work_experiences')
    role = models.CharField(_("Cargo"), max_length=255)
    company = models.CharField(_("Empresa"), max_length=255)
    start_date = models.DateField(_("Data de Início"))
    end_date = models.DateField(_("Data de Término"), blank=True, null=True) # Null if current job
    responsibilities = models.TextField(_("Principais Atividades/Responsabilidades"), blank=True, null=True)

    def __str__(self):
        return f"{self.role} @ {self.company}"

    class Meta:
        verbose_name = _("Experiência Profissional")
        verbose_name_plural = _("Experiências Profissionais")
        ordering = ['-start_date']

