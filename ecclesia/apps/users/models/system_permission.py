import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class SystemPermission(models.Model):
    """
    Representa uma permissão disponível no sistema.
    Estas permissões são globais e independentes de qualquer igreja.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(_('Código da permissão'), max_length=100, unique=True, blank=False, null=False, db_index=True, help_text=_('Ex: members.view, members.create, church.update'))
    name = models.CharField(_('Nome'), max_length=150, blank=False, null=False, help_text=_('Ex: Visualizar membros, Criar membros'))
    module = models.CharField(_('Módulo'), max_length=50, db_index=True, help_text=_('Ex: members, church, finance, events'))
    description = models.TextField(_('Descrição'), blank=True,null=True, default='', help_text=_('Descrição detalhada do que esta permissão permite'))
    is_active = models.BooleanField(_('Ativo'), default=True, help_text=_('Desative para remover a permissão do sistema sem deletá-la'))
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Permissão do Sistema')
        verbose_name_plural = _('Permissões do Sistema')
        ordering = ['module', 'code']

        constraints = [
            models.UniqueConstraint(fields=['code'], name='unique_system_permission_code')
        ]

        indexes = [
            models.Index(fields=['module']),
            models.Index(fields=['code']),
            models.Index(fields=['module', 'is_active']),
        ]

    def __str__(self):
        return f"[{self.module}] {self.name} ({self.code})"
