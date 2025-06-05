from django.db import models
from django.utils.translation import gettext_lazy as _

# Choices for address state (Brazilian UFs) - Reusing from accounts.models if needed, or define here
UF_CHOICES = [
    ("AC", "Acre"), ("AL", "Alagoas"), ("AP", "Amapá"), ("AM", "Amazonas"),
    ("BA", "Bahia"), ("CE", "Ceará"), ("DF", "Distrito Federal"), ("ES", "Espírito Santo"),
    ("GO", "Goiás"), ("MA", "Maranhão"), ("MT", "Mato Grosso"), ("MS", "Mato Grosso do Sul"),
    ("MG", "Minas Gerais"), ("PA", "Pará"), ("PB", "Paraíba"), ("PR", "Paraná"),
    ("PE", "Pernambuco"), ("PI", "Piauí"), ("RJ", "Rio de Janeiro"), ("RN", "Rio Grande do Norte"),
    ("RS", "Rio Grande do Sul"), ("RO", "Rondônia"), ("RR", "Roraima"), ("SC", "Santa Catarina"),
    ("SP", "São Paulo"), ("SE", "Sergipe"), ("TO", "Tocantins")
]

class HospitalUnit(models.Model):
    name = models.CharField(_("Nome da Unidade Hospitalar"), max_length=255)
    city = models.CharField(_("Cidade"), max_length=100)
    state = models.CharField(_("Estado"), max_length=2, choices=UF_CHOICES)
    address = models.TextField(_("Endereço Completo"), blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.city}/{self.state}"

    class Meta:
        verbose_name = _("Unidade Hospitalar")
        verbose_name_plural = _("Unidades Hospitalares")
        ordering = ["name"]

class Department(models.Model):
    name = models.CharField(_("Nome do Setor"), max_length=255)
    hospital_unit = models.ForeignKey(HospitalUnit, on_delete=models.CASCADE, related_name='departments', verbose_name=_("Unidade Hospitalar"))

    def __str__(self):
        return f"{self.name} ({self.hospital_unit.name})"

    class Meta:
        verbose_name = _("Setor")
        verbose_name_plural = _("Setores")
        ordering = ["hospital_unit__name", "name"]
        unique_together = [("name", "hospital_unit")] # Ensure department name is unique within a hospital unit

