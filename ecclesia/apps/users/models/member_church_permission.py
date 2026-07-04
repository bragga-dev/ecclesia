import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.models.system_permission import SystemPermission
from django.utils import timezone
from ecclesia.apps.users.models.user import User

class MemberChurchPermission(models.Model):
    """
    Permissões atribuídas diretamente a um MemberChurch (vínculo específico).    
    Isso permite que um mesmo MemberChurch (vínculo específico) tenha permissões diferentes em igrejas diferentes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    member_church = models.ForeignKey(MemberChurch, on_delete=models.CASCADE, related_name='permissions', verbose_name=_('Vínculo Membro-Igreja'))
    permission = models.ForeignKey(SystemPermission, on_delete=models.CASCADE, related_name='member_church_permissions', verbose_name=_('Permissão'))
    is_active = models.BooleanField(_('Ativo'), default=True, help_text=_('Desative para remover temporariamente esta permissão'))
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_permissions', verbose_name=_('Concedido por'))
    granted_at = models.DateTimeField(_('Concedido em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    expires_at = models.DateTimeField(_('Expira em'), null=True, blank=True, help_text=_('Deixe em branco para permissão permanente'))
    
    class Meta:
        verbose_name = _('Permissão do Membro na Igreja')
        verbose_name_plural = _('Permissões dos Membros nas Igrejas')
        constraints = [
            models.UniqueConstraint(
                fields=['member_church', 'permission'],
                name='unique_member_church_permission'
            )
        ]
        
        indexes = [
            models.Index(fields=['member_church', 'permission']),
            models.Index(fields=['member_church', 'is_active']),
            models.Index(fields=['permission', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.member_church.member} @ {self.member_church.church} → {self.permission.name}"
    
    def clean(self):
        if not self.permission.is_active:
            raise ValidationError({
                'permission': _('Não é possível atribuir uma permissão inativa.')
            })
        
        if self.member_church.status != MemberChurch.Status.ACTIVE:
            raise ValidationError({
                'member_church': _('Não é possível atribuir permissões a um vínculo inativo.')
            })
    
    @property
    def is_expired(self) -> bool:
        """Verifica se a permissão expirou."""
        if not self.expires_at:
            return False
       
        return timezone.now() > self.expires_at
    
    @property
    def is_effective(self) -> bool:
        """Verifica se a permissão está efetivamente ativa."""
        return self.is_active and not self.is_expired and self.permission.is_active
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    