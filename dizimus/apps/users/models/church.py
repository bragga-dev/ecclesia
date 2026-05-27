from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from encrypted_model_fields.fields import EncryptedTextField

from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cnpj
from dizimus.apps.users.validators.validate_image_file import validate_image_file
from .user import User
from .base_address import BaseAddress


# ─────────────────────────────────────────────────────────────────────────────
# Upload path
# Gera: church_banners/<user_id>/banner.jpg  no bucket dizimus-media.
# ─────────────────────────────────────────────────────────────────────────────

def church_banner_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"church_banners/{instance.user_id}/banner.{ext}"


# Arquivo que deve existir no bucket:
#   mc cp default/banner.jpg local/dizimus-media/default/banner.jpg
DEFAULT_CHURCH_BANNER = "default/banner.jpg"


class Church(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="church",
    )
    is_verified = models.BooleanField(_('Autorizado?'), default=False)
    cnpj = models.CharField(
        max_length=18, unique=True, null=True, blank=True,
        validators=[validate_cnpj],
        help_text=_('Formato: 00.000.000/0000-00.'),
    )
    asaas_token = EncryptedTextField(
        null=True, blank=True,
        help_text=_('Token de acesso à API do Asaas.'),
    )
    total_members = models.PositiveIntegerField(
        _('Total de membros'), null=True, blank=True, default=0,
    )
    instagram = models.URLField(_('Instagram'), max_length=255, null=True, blank=True)
    website   = models.URLField(_('Site'),      max_length=255, null=True, blank=True)
    about     = models.TextField(
        _('Sobre'), null=True, blank=True,
        help_text=_('Descrição da igreja. Máx: 1000 caracteres.'),
    )
    banner = models.ImageField(
        upload_to=church_banner_path,
        default=DEFAULT_CHURCH_BANNER,
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text=_('Formatos aceitos: jpg, jpeg ou png. Máx: 5MB.'),
    )

    class Meta:
        verbose_name        = "Igreja"
        verbose_name_plural = "Igrejas"

    def __str__(self):
        return self.user.get_full_name()

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def has_valid_asaas_token(self) -> bool:
        return bool(self.asaas_token and self.asaas_token.strip())

    @property
    def banner_url(self) -> str:
        """
        Retorna a URL do banner no MinIO com fallback seguro.
        Use {{ church.banner_url }} nos templates.
        """
        if self.banner and self.banner.name != DEFAULT_CHURCH_BANNER:
            try:
                return self.banner.url
            except Exception:
                pass
        return f"{settings.MEDIA_URL}{DEFAULT_CHURCH_BANNER}"

    # ── Métodos de negócio ────────────────────────────────────────────────────

    def refresh_total_members(self) -> None:
        # Import local evita circular import (MemberChurch → Church → MemberChurch)
        from dizimus.apps.community.models.member_church import MemberChurch
        self.total_members = (
            self.member_memberships
            .filter(status=MemberChurch.Status.ACTIVE)
            .count()
        )
        self.save(update_fields=['total_members'])

    def save(self, *args, **kwargs):
        if not self.banner:
            self.banner = DEFAULT_CHURCH_BANNER
        super().save(*args, **kwargs)


class ChurchAddress(BaseAddress):
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name='addresses',
    )

    def save(self, *args, **kwargs):
        if self.principal:
            ChurchAddress.objects.filter(
                church=self.church, principal=True,
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)