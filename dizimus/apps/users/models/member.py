import uuid
import re
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.utils.text import slugify
from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cpf
from .user import User
from .base_address import BaseAddress
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import parse, format_number, PhoneNumberFormat


class Member(models.Model):
    class ContributionType(models.TextChoices):
        NONE = "none", "Nenhum"
        DIZIMISTA = "dizimista", "Dizimista"
        OFERTANTE = "ofertante", "Ofertante"
        BOTH = "both", "Dizimista e Ofertante"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member",)
    first_name = models.CharField(_('Primeiro nome'), max_length=150, blank=True, null=True, default="")
    last_name  = models.CharField(_('Sobrenome'), max_length=150, blank=True, null=True, default="")
    username = models.CharField(_('Nome de usuário'), max_length=30, unique=True, blank=True, null=True,)
    phone = PhoneNumberField(region="BR", blank=True, default="", null=False, help_text=_('Número de telefone no formato internacional, ex: +55 11 99999-8888.'),)
    help_text=_('Obrigatório. 15 caracteres ou menos. Letras, dígitos e @/./+/-/_ apenas.'), 
    validators=[validators.RegexValidator(re.compile(r'^[\w.@+-]+$'), _('Entre com um nome de usuário válido.'), _('inválido'))]
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True, validators=[validate_cpf],  help_text=_('Formato: 000.000.000-00.'),)
    slug  = models.SlugField(max_length=255, unique=True, editable=False, null=True, blank=True)
    contribution_type = models.CharField(_('Tipo de contribuição'), max_length=20, choices=ContributionType.choices, default=ContributionType.NONE)
    date_of_birth = models.DateField(_('Data de nascimento'), null=True, blank=True, help_text=_('Formato: DD/MM/AAAA.'),)

    class Meta:
        verbose_name        = "Membro"
        verbose_name_plural = "Membros"

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username or f"Membro {self.id}"

    def __str__(self):
        return self.first_name or f"Membro {self.id}"
    
    @staticmethod
    def normalize_phone(phone_str: str) -> str:
        number = parse(phone_str, "BR")
        return format_number(number, PhoneNumberFormat.E164)

    def clean(self):
        if self.date_of_birth and self.date_of_birth > timezone.localdate():
            raise ValidationError(
                {'date_of_birth': _('Data de nascimento não pode ser no futuro.')}
            )
        
    def has_name_changed(self) -> bool:
        if not self.pk or self._state.adding:
            return False
        old = Member.objects.filter(pk=self.pk).only('first_name', 'last_name', 'username').first()
        if not old:
            return True
        return (
            old.first_name != self.first_name or
            old.last_name  != self.last_name or
            old.username   != self.username
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.slug or self._state.adding or self.has_name_changed():
            base_slug   = slugify(self.get_full_name()) or str(self.id)
            unique_slug = base_slug
            num = 1
            while Member.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class MemberAddress(BaseAddress):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='addresses',
    )

    def save(self, *args, **kwargs):
        if self.principal:
            MemberAddress.objects.filter(
                member=self.member, principal=True,
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)


