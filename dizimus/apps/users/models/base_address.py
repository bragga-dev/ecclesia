import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from dizimus.apps.users.validators.validate_cep import validar_cep


class BaseAddress(models.Model):
    class States(models.TextChoices):
        AC = "AC", "Acre"
        AL = "AL", "Alagoas"
        AP = "AP", "Amapá"
        AM = "AM", "Amazonas"
        BA = "BA", "Bahia"
        CE = "CE", "Ceará"
        DF = "DF", "Distrito Federal"
        ES = "ES", "Espírito Santo"
        GO = "GO", "Goiás"
        MA = "MA", "Maranhão"
        MT = "MT", "Mato Grosso"
        MS = "MS", "Mato Grosso do Sul"
        MG = "MG", "Minas Gerais"
        PA = "PA", "Pará"
        PB = "PB", "Paraíba"
        PR = "PR", "Paraná"
        PE = "PE", "Pernambuco"
        PI = "PI", "Piauí"
        RJ = "RJ", "Rio de Janeiro"
        RN = "RN", "Rio Grande do Norte"
        RS = "RS", "Rio Grande do Sul"
        RO = "RO", "Rondônia"
        RR = "RR", "Roraima"
        SC = "SC", "Santa Catarina"
        SP = "SP", "São Paulo"
        SE = "SE", "Sergipe"
        TO = "TO", "Tocantins"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cep        = models.CharField(_('CEP'), max_length=9, validators=[validar_cep])
    road       = models.CharField(_('Rua'), max_length=255)
    number     = models.CharField(_('N°'), max_length=10)
    district   = models.CharField(_('Bairro'), max_length=100)
    city       = models.CharField(_('Cidade'), max_length=100)
    state      = models.CharField(_('Estado'), max_length=2, choices=States.choices)
    country    = models.CharField(_('País'), max_length=100, default="Brasil")
    complement = models.CharField(_('Complemento'), max_length=255, null=True, blank=True)
    principal  = models.BooleanField(_('Endereço Padrão?'), default=True)
    slug       = models.SlugField(max_length=255, unique=True, editable=False)

    class Meta:
        verbose_name        = "Endereço"
        verbose_name_plural = "Endereços"
        abstract = True

    def __str__(self):
        return f"{self.road}, {self.number} - {self.city}/{self.state}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                f"{self.road}-{self.number}-{self.district}"
                f"-{self.city}-{self.state}-{str(self.id)[:8]}"
            )
            unique_slug = base_slug
            num = 1
            while (
                self.__class__.objects
                .filter(slug=unique_slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)