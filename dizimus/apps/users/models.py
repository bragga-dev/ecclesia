import re
import uuid
from django.db import models
from django.core import validators
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import parse, format_number, PhoneNumberFormat
from dizimus.apps.users.validators.validate_cpf_cnpj import  validate_cpf, validate_cnpj
from dizimus.apps.users.validators.validate_image_file import validate_image_file
from dizimus.apps.users.validators.validate_cep import validar_cep
from encrypted_model_fields.fields import EncryptedTextField


# ─────────────────────────────────────────────────────────────────────────────
# Callables de upload_to
# Geram caminhos organizados no bucket, ex: photos/uuid/nome-do-arquivo.jpg
# Isso evita colisões e facilita gerenciar/remover arquivos por usuário.
# ─────────────────────────────────────────────────────────────────────────────

def user_photo_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"photos/{instance.id}/photo.{ext}"


def church_banner_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower()
    return f"church_banners/{instance.user_id}/banner.{ext}"


# ─────────────────────────────────────────────────────────────────────────────
# Imagens padrão
# Com MinIO/S3 o campo `default` é um caminho relativo dentro do bucket.
# Faça o upload manual desses arquivos para o bucket dizimus-media:
#   mc cp default/user_img.jpg local/dizimus-media/default/user_img.jpg
#   mc cp default/banner.jpg   local/dizimus-media/default/banner.jpg
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_USER_PHOTO  = "default/user_img.jpg"
DEFAULT_CHURCH_BANNER = "default/banner.jpg"


class UserManager(BaseUserManager):

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O e-mail é obrigatório.'))

        email = self.normalize_email(email)

        role = extra_fields.get('role', User.UserRole.MEMBER)

        # ─────────────────────────────────────────────
        # ADMIN ROOT
        # ─────────────────────────────────────────────
        if role == User.UserRole.ADMIN:
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)
            extra_fields.setdefault('is_active', True)
            extra_fields.setdefault('is_trusty', True)

        # ─────────────────────────────────────────────
        # MEMBER e CHURCH
        # Necessitam confirmação/aprovação
        # ─────────────────────────────────────────────
        else:
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
            extra_fields.setdefault('is_active', False)
            extra_fields.setdefault('is_trusty', False)

        user = self.model(
            email=email,
            last_login=timezone.now(),
            date_joined=timezone.now(),
            **extra_fields,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Cria MEMBER ou CHURCH.
        ADMIN só pode ser criado via create_superuser.
        """

        role = extra_fields.get('role', User.UserRole.MEMBER)

        if role == User.UserRole.ADMIN:
            raise ValueError(
                _('Use create_superuser para criar administradores.')
            )

        extra_fields.setdefault('role', User.UserRole.MEMBER)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria ADMIN ROOT.
        Usado pelo comando:
        python manage.py createsuperuser
        """

        extra_fields.setdefault('role', User.UserRole.ADMIN)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_trusty', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser deve ter is_staff=True.'))

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser deve ter is_superuser=True.'))

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class UserRole(models.TextChoices):
        ADMIN  = "admin", "Administrador Root"
        MEMBER = "member", "Membro"
        CHURCH = "church", "Igreja"

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username   = models.CharField(
        _('username'), max_length=15, unique=True,
        help_text=_('Obrigatório. 15 caracteres ou menos. Letras, dígitos e @/./+/-/_ apenas.'),
        validators=[validators.RegexValidator(
            re.compile(r'^[\w.@+-]+$'),
            _('Entre com um nome de usuário válido.'),
            _('inválido'),
        )],
    )
    role       = models.CharField(
        _("Tipo de usuário"), max_length=20,
        choices=UserRole.choices, default=UserRole.MEMBER,
    )
    first_name = models.CharField(_('Primeiro nome'), max_length=100)
    last_name  = models.CharField(_('Sobrenome'), max_length=100, blank=True)
    email      = models.EmailField(_('E-mail'), max_length=255, unique=True)

    # ── Foto ─────────────────────────────────────────────────────────────────
    # upload_to agora é um callable → gera: photos/<uuid>/photo.jpg no MinIO.
    # default aponta para um arquivo que deve existir no bucket dizimus-media.
    photo = models.ImageField(
        upload_to=user_photo_path,
        default=DEFAULT_USER_PHOTO,
        blank=True,
        null=True,
        validators=[validate_image_file],
        help_text=_('Formatos aceitos: jpg, jpeg ou png. Máx: 5MB.'),
    )

    phone       = PhoneNumberField(region="BR", blank=True, default="", null=False, help_text=_('Número de telefone no formato internacional, ex: +55 11 99999-8888.'))
    slug        = models.SlugField(max_length=255, unique=True, editable=False)
    is_staff    = models.BooleanField(_('Staff'), default=False)
    is_active   = models.BooleanField(_('Ativo?'), default=False)
    is_trusty   = models.BooleanField(_('Confiável?'), default=False)
    date_joined = models.DateTimeField(_('Data de admissão'), default=timezone.now)
    created_at  = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at  = models.DateTimeField(_('Atualizado em'), auto_now=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name        = _('Usuário')
        verbose_name_plural = _('Usuários')

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    @property
    def is_member(self):
        return self.role == self.UserRole.MEMBER

    @property
    def is_church(self):
        return self.role == self.UserRole.CHURCH

    # ── URL da foto (com fallback seguro para o MinIO) ────────────────────────
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
        # Monta URL pública da imagem padrão diretamente
        from django.conf import settings
        return f"{settings.MEDIA_URL}{DEFAULT_USER_PHOTO}"

    def has_name_changed(self) -> bool:
        if not self.pk or self._state.adding:
            return False
        old = User.objects.filter(pk=self.pk).only('first_name', 'last_name').first()
        if not old:
            return True
        return old.first_name != self.first_name or old.last_name != self.last_name

    def __str__(self):
        return self.email
    
    

    def normalize_phone(phone_str: str) -> str:
        number = parse(phone_str, "BR")
        return format_number(number, PhoneNumberFormat.E164)

    
    def clean(self):
        super().clean()
        if self.role == self.UserRole.MEMBER and not self.last_name:
            raise ValidationError({"last_name": _("Sobrenome é obrigatório para membros.")})

    def save(self, *args, **kwargs):
        self.full_clean()

        # Slug: regenera ao criar ou ao trocar o nome
        if not self.slug or self._state.adding or self.has_name_changed():
            base_slug   = slugify(self.get_full_name()) or str(self.id)
            unique_slug = base_slug
            num = 1
            while User.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug

        if not self.photo:
            self.photo = DEFAULT_USER_PHOTO

        super().save(*args, **kwargs)


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
            while self.__class__.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)




class Church(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name="church")
    is_verified   = models.BooleanField(_('Autorizado?'), default=False)
    cnpj          = models.CharField( max_length=18, unique=True, null=True, blank=True, validators=[validate_cnpj], help_text=_('Formato: 00.000.000/0000-00.'))
    asaas_token   = EncryptedTextField(null=True, blank=True, help_text=_('Token de acesso à API do Asaas.'))
    total_members = models.PositiveIntegerField(_('Total de membros'), null=True, blank=True, default=0)
    instagram     = models.URLField(_('Instagram'), max_length=255, null=True, blank=True)
    website       = models.URLField(_('Site'), max_length=255, null=True, blank=True)
    about         = models.TextField(_('Sobre'), null=True, blank=True, help_text=_('Descrição da igreja. Máx: 1000 caracteres.'))

    
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
        from django.conf import settings
        return f"{settings.MEDIA_URL}{DEFAULT_CHURCH_BANNER}"
    
    def refresh_total_members(self) -> None:
        self.total_members = self.member_memberships.filter(status=MemberChurch.Status.ACTIVE).count()
        self.save(update_fields=['total_members'])

    def save(self, *args, **kwargs):
        if not self.banner:
            self.banner = DEFAULT_CHURCH_BANNER
        super().save(*args, **kwargs)


class ChurchAddress(BaseAddress):
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='addresses')

    def save(self, *args, **kwargs):
        if self.principal:
            ChurchAddress.objects.filter(
                church=self.church, principal=True
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)


class Member(models.Model):
    user          = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member")
    cpf           = models.CharField(max_length=14, unique=True, null=True, blank=True,  validators=[validate_cpf], help_text=_('Formato: 000.000.000-00.'))
    date_of_birth = models.DateField(_('Data de nascimento'), null=True, blank=True,  help_text=_('Formato: DD/MM/AAAA.'),)  

    def clean(self):
        if self.date_of_birth and self.date_of_birth > timezone.localdate():
            raise ValidationError(
                {'date_of_birth': _('Data de nascimento não pode ser no futuro.')}
            )

    class Meta:
        verbose_name        = "Membro"
        verbose_name_plural = "Membros"

    def __str__(self):
        return self.user.get_full_name()


class MemberAddress(BaseAddress):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='addresses')

    def save(self, *args, **kwargs):
        if self.principal:
            MemberAddress.objects.filter(
                member=self.member, principal=True
            ).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)


class MemberChurch(models.Model):
    class Role(models.TextChoices):
        MEMBER       = "member", "Membro"
        PASTOR       = "pastor/padre", "Pastor/Padre"
        TREASURER    = "tesoureiro", "Tesoureiro"
        SECRETARY    = "secretário", "Secretário"
        CHURCH_ADMIN = "admin", "Administrador"

    class Status(models.TextChoices):
        ACTIVE   = "active", "Ativo"
        INACTIVE = "inactive", "Inativo"
        PENDING  = "pending", "Pendente"

    role = models.CharField(_('Função'), max_length=30, choices=Role.choices, default=Role.MEMBER, db_index=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='church_memberships')
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='member_memberships')
    status = models.CharField(_('Status'), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    joined_at = models.DateTimeField(_('Data de adesão'), auto_now_add=True, editable=False, help_text=_('Data e hora em que o membro se vinculou à igreja.'))
    left_at = models.DateTimeField(_('Data de saída'), null=True, blank=True, help_text=_('Data e hora em que o membro se desvinculou da igreja. Deixe em branco se ainda for membro.'))

    class Meta:
        unique_together = ('member', 'church')
        verbose_name        = "Vínculo Membro-Igreja"
        verbose_name_plural = "Vínculos Membro-Igreja"
        ordering = ['-joined_at']
        
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'church'],
                name='unique_member_church'
            )
        ]

        indexes = [
            models.Index(fields=['member', 'church']),
            models.Index(fields=['church', 'role']),
            models.Index(fields=['church', 'status']),
        ]

    def __str__(self):
        return f"{self.member} - {self.church} ({self.role})"