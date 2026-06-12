import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from dizimus.apps.users.models.member import Member
from dizimus.apps.users.models.church import Church



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

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='church_memberships')
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='member_memberships')
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(_('Função'), max_length=30, choices=Role.choices, default=Role.MEMBER, db_index=True,)
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True,)
    joined_at = models.DateTimeField(_('Data de adesão'), auto_now_add=True, editable=False, help_text=_('Data e hora em que o membro se vinculou à igreja.'), )
    left_at = models.DateTimeField(_('Data de saída'), null=True, blank=True, help_text=_('Data e hora em que o membro se desvinculou da igreja. Deixe em branco se ainda for membro.'), )

    class Meta:
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