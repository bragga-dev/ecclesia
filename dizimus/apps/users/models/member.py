from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cpf
from .user import User
from .base_address import BaseAddress


class Member(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="member",
    )
    cpf = models.CharField(
        max_length=14, unique=True, null=True, blank=True,
        validators=[validate_cpf],
        help_text=_('Formato: 000.000.000-00.'),
    )
    date_of_birth = models.DateField(
        _('Data de nascimento'), null=True, blank=True,
        help_text=_('Formato: DD/MM/AAAA.'),
    )

    class Meta:
        verbose_name        = "Membro"
        verbose_name_plural = "Membros"

    def __str__(self):
        return self.user.get_full_name()

    def clean(self):
        if self.date_of_birth and self.date_of_birth > timezone.localdate():
            raise ValidationError(
                {'date_of_birth': _('Data de nascimento não pode ser no futuro.')}
            )


class MemberAddress(BaseAddress):
    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='addresses',
    )

    def save(self, *args, **kwargs):
        if self.principal:
            MemberAddress.objects.filter(
                member=self.member, principal=True,
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)


class MemberChurch(models.Model):
    class Role(models.TextChoices):
        MEMBER       = "member",      "Membro"
        PASTOR       = "pastor/padre","Pastor/Padre"
        TREASURER    = "tesoureiro",  "Tesoureiro"
        SECRETARY    = "secretário",  "Secretário"
        CHURCH_ADMIN = "admin",       "Administrador"

    class Status(models.TextChoices):
        ACTIVE   = "active",   "Ativo"
        INACTIVE = "inactive", "Inativo"
        PENDING  = "pending",  "Pendente"

    member = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name='church_memberships',
    )
    # Church é referenciado como string para quebrar dependência circular
    # (Church importa MemberChurch.Status → Member importa Church = ciclo).
    church = models.ForeignKey(
        'users.Church', on_delete=models.CASCADE, related_name='member_memberships',
    )
    role = models.CharField(
        _('Função'), max_length=30,
        choices=Role.choices, default=Role.MEMBER, db_index=True,
    )
    status = models.CharField(
        _('Status'), max_length=20,
        choices=Status.choices, default=Status.PENDING, db_index=True,
    )
    joined_at = models.DateTimeField(
        _('Data de adesão'), auto_now_add=True, editable=False,
        help_text=_('Data e hora em que o membro se vinculou à igreja.'),
    )
    left_at = models.DateTimeField(
        _('Data de saída'), null=True, blank=True,
        help_text=_('Data e hora em que o membro se desvinculou da igreja. Deixe em branco se ainda for membro.'),
    )

    class Meta:
        unique_together     = ('member', 'church')
        verbose_name        = "Vínculo Membro-Igreja"
        verbose_name_plural = "Vínculos Membro-Igreja"
        ordering            = ['-joined_at']

        constraints = [
            models.UniqueConstraint(
                fields=['member', 'church'],
                name='unique_member_church',
            )
        ]

        indexes = [
            models.Index(fields=['member', 'church']),
            models.Index(fields=['church', 'role']),
            models.Index(fields=['church', 'status']),
        ]

    def __str__(self):
        return f"{self.member} - {self.church} ({self.role})"