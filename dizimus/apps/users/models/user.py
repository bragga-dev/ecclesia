import re
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import parse, format_number, PhoneNumberFormat

from dizimus.apps.users.validators.validate_image_file import validate_image_file
from dizimus.apps.users.models.constants import ROLE_ADMIN, ROLE_MEMBER, ROLE_CHURCH
from dizimus.apps.users.models.user_manage import UserManager

# ─────────────────────────────────────────────────────────────────────────────
# Upload path
# Gera: photos/<uuid>/photo.jpg  no bucket dizimus-media.
# ─────────────────────────────────────────────────────────────────────────────

def user_photo_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"photos/{instance.id}/photo.{ext}"


# Arquivo que deve existir no bucket:
#   mc cp default/user_img.jpg local/dizimus-media/default/user_img.jpg
DEFAULT_USER_PHOTO = "default/user_img.jpg"


class User(AbstractBaseUser, PermissionsMixin):
    class UserRole(models.TextChoices):
        ADMIN  = ROLE_ADMIN,  "Administrador Root"
        MEMBER = ROLE_MEMBER, "Membro"
        CHURCH = ROLE_CHURCH, "Igreja"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    role = models.CharField(
        _("Tipo de usuário"), max_length=20,
        choices=UserRole.choices, default=UserRole.MEMBER,
    )

    email      = models.EmailField(_('E-mail'), max_length=255, unique=True)

    # ── Foto ──────────────────────────────────────────────────────────────────
    # upload_to é callable → gera: photos/<uuid>/photo.jpg no MinIO.
    # default aponta para arquivo que deve existir no bucket dizimus-media.
    photo = models.ImageField(
        upload_to=user_photo_path,
        default=DEFAULT_USER_PHOTO,
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text=_('Formatos aceitos: jpg, jpeg ou png. Máx: 5MB.'),
    )

    phone = PhoneNumberField(
        region="BR", blank=True, default="", null=False,
        help_text=_('Número de telefone no formato internacional, ex: +55 11 99999-8888.'),
    )

    slug      = models.SlugField(max_length=255, unique=True, editable=False)
    is_staff  = models.BooleanField(_('Staff'), default=False)
    is_active = models.BooleanField(_('Ativo?'), default=False)
    is_trusty = models.BooleanField(_('Confiável?'), default=False)

    date_joined = models.DateTimeField(_('Data de admissão'), default=timezone.now)
    created_at  = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Atualizado em'), auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name        = _('Usuário')
        verbose_name_plural = _('Usuários')

    # ── Helpers básicos ───────────────────────────────────────────────────────

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def __str__(self):
        return self.email

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def is_member(self):
        return self.role == self.UserRole.MEMBER

    @property
    def is_church(self):
        return self.role == self.UserRole.CHURCH

    @property
    def photo_url(self) -> str:
        """
        Retorna a URL da foto no MinIO.
        Nunca lança erro: se a foto não existir no bucket, devolve a URL do padrão.
        Use {{ user.photo_url }} nos templates em vez de {{ user.photo.url }}.
        """
        if self.photo and self.photo.name != DEFAULT_USER_PHOTO:
            try:
                return self.photo.url
            except Exception:
                pass
        return f"{settings.MEDIA_URL}{DEFAULT_USER_PHOTO}"

    # ── Utilitários internos ──────────────────────────────────────────────────

    @staticmethod
    def normalize_phone(phone_str: str) -> str:
        number = parse(phone_str, "BR")
        return format_number(number, PhoneNumberFormat.E164)


    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.photo:
            self.photo = DEFAULT_USER_PHOTO
        super().save(*args, **kwargs)