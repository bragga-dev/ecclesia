from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from encrypted_model_fields.fields import EncryptedTextField
from django.db.models import UniqueConstraint
from dizimus.apps.users.validators.validate_cpf_cnpj import validate_cnpj
from dizimus.apps.users.validators.validate_image_file import validate_image_file
from .user import User
from .base_address import BaseAddress
from django.utils.text import slugify


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
    class ChurchType(models.TextChoices):
        HEADQUARTERS = "headquarters", "Sede/Matriz"
        COMMUNITY = "community", "Comunidade"
        INDEPENDENT = "independent", "Independente"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="church",)
    parent_church = models.ForeignKey("self", on_delete=models.SET_NULL,  null=True, blank=True, related_name="child_churches",)
    full_name = models.CharField(_("Nome Completo da Instituição"), max_length=255, blank=True, null=True, help_text=_('Ex: Igreja Batista da Paz.'), default="")
    is_verified = models.BooleanField(_('Autorizado?'), default=False)
    cnpj = models.CharField(max_length=18, unique=False, null=True, blank=True,  validators=[validate_cnpj], help_text=_('Formato: 00.000.000/0000-00.'),)
    asaas_token = EncryptedTextField( null=True, blank=True,  help_text=_('Token de acesso à API do Asaas.'),)
    total_members = models.PositiveIntegerField(_('Total de membros'), null=True, blank=True, default=0,)
    church_type = models.CharField(max_length=20, choices=ChurchType.choices, default=ChurchType.INDEPENDENT,)
    instagram = models.URLField(_('Instagram'), max_length=255, null=True, blank=True)
    website   = models.URLField(_('Site'),      max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, editable=False, null=True, blank=True)
    about     = models.TextField(_('Sobre'), null=True, blank=True, help_text=_('Descrição da igreja. Máx: 1000 caracteres.'),)
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
        constraints = [
            UniqueConstraint(
                fields=["cnpj", "full_name"],
                name="unique_church_per_cnpj_name"
            )
        ]

    def __str__(self):
        return self.full_name or f"Igreja {self.id}"

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
        return self.banner.storage.url(DEFAULT_CHURCH_BANNER)

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


    def has_name_changed(self) -> bool:
        if not self.pk or self._state.adding:
            return False
        old = Church.objects.filter(pk=self.pk).only('full_name').first()
        if not old:
            return True
        return (old.full_name != self.full_name)

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.banner:
            self.banner = DEFAULT_CHURCH_BANNER
        if not self.slug or self._state.adding or self.has_name_changed():
            base_slug = slugify(self.full_name or str(self.id))
            unique_slug = base_slug
            num = 1
            while Church.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

class ChurchAddress(BaseAddress):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    church = models.ForeignKey(
        Church, on_delete=models.CASCADE, related_name='addresses',
    )

    def save(self, *args, **kwargs):
        if self.principal:
            ChurchAddress.objects.filter(
                church=self.church, principal=True,
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)