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
from validate_docbr import CPF, CNPJ
from phonenumber_field.modelfields import PhoneNumberField
from users.validators import validate_image_file, validar_cep



class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError(_('O endereço de email deve ser fornecido.'))
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user
    

class User(AbstractBaseUser, PermissionsMixin):
    class UserRole(models.TextChoices):

        ADMIN = "admin", "Admin"
        MEMBER = "member", "Membro"
        CHURCH = "church", "Igreja"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    username = models.CharField( _('username'), max_length=15, unique=True,  help_text=_('Obrigatório. 15 caracteres ou menos. Letras, dígitos e @/./+/-/_ apenas.'), validators=[validators.RegexValidator(re.compile(r'^[\w.@+-]+$'), _('Entre com um nome de usuário válido.'), _('inválido'))],)
    role = models.CharField(_("Tipo de usuário"),  max_length=20, choices=UserRole.choices, default=UserRole.MEMBER, help_text=_('Selecione o tipo de usuário.'))
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    photo = models.ImageField(upload_to="photos/", default="default/user_img.jpg", blank=True, null=True, validators=[validate_image_file], help_text=_('Formato de arquivo: jpg, jpeg ou png.'))  
    phone = PhoneNumberField(region="BR", unique=True, null=True, blank=True, help_text='Digite um número com DDD. Ex: +55 11 91234-5678')
    slug = models.SlugField(max_length=255, unique=True, editable=False)
    is_staff = models.BooleanField(_('Staff'), default=False,  help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('Ativo?'), default=True,  help_text=_('Indica se este usuário está ativo ou não.'))
    date_joined = models.DateTimeField(_('Data de admissão'), default=timezone.now)
    is_trusty = models.BooleanField(_('trusty'), default=False, help_text=_('Indica se este usuário é confiável ou não.'))
    created_at = models.DateTimeField(_('Data de criação'), auto_now_add=True) 
    updated_at = models.DateTimeField(_('Última atualização'), auto_now=True)  

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')

    def get_full_name(self):
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])
    
    @property
    def is_admin(self):
        return self.role == self.UserRole.ADMIN

    @property
    def is_member(self):
        return self.role == self.UserRole.MEMBER

    @property
    def is_church(self):
        return self.role == self.UserRole.CHURCH
    
    def has_name_changed(self):
        if not self.id:
            return False
            
        old_user = User.objects.filter(id=self.id).first()
        if not old_user:
            return True
            
        return (old_user.first_name != self.first_name or old_user.last_name != self.last_name)
    
    def __str__(self):
        return self.email 
          
    def save(self, *args, **kwargs):
        self.full_clean()
        if (not self.slug  or self._state.adding  or self.has_name_changed()):
            base_slug = (slugify(self.get_full_name())  or str(self.id))
            unique_slug = base_slug
            num = 1

            while (User.objects .filter(slug=unique_slug) .exclude(pk=self.pk).exists()):
                unique_slug = (f'{base_slug}-{num}')
                num += 1
            self.slug = unique_slug
        if not self.photo:
            self.photo = (self._meta .get_field("photo").default)

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


        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        cep = models.CharField(_('CEP'), max_length=9, null=False, blank=False, validators=[validar_cep])  
        road = models.CharField(_('Rua'), max_length=255, null=False, blank=False)
        number = models.CharField(_('N°'), max_length=10, null=False, blank=False)
        district = models.CharField(_('Bairro'), max_length=100, null=False, blank=False)
        city = models.CharField(_('Cidade'), max_length=100, null=False, blank=False)
        state = models.CharField(_('Estado'),  max_length=2, choices=States.choices, null=False,  blank=False)
        country = models.CharField(_('País'), max_length=100, default="Brasil")
        principal = models.BooleanField(_('Endereço Padrão?'), default=True)
        slug = models.SlugField(max_length=255, unique=True, editable=False)
        complement = models.CharField(_('Complemento'), max_length=255, null=True, blank=True)

        def __str__(self):
            return f"{self.road}, {self.number} - {self.city}/{self.state}"
    
        
        class Meta:
            verbose_name = "Endereço"
            verbose_name_plural =  "Endereços"
            abstract = True
            
        def save(self, *args, **kwargs):
            if not self.slug:
                base_slug = slugify(f"{self.road}-{self.number}-{self.district}-{self.city}-{self.state}-{self.country}")
                unique_slug = base_slug
                num = 1
                while self.__class__.objects.filter(slug=unique_slug).exists():
                    unique_slug = f'{base_slug}-{num}'
                    num += 1
                self.slug = unique_slug
            super().save(*args, **kwargs)


class Church(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="church")
    is_verified = models.BooleanField(_('Autorizado?'), default=False, help_text="Indica se a igreja foi verificada pela plataforma.")
    cnpj = models.CharField(max_length=18, unique=True, null=True, blank=True)
    banner = models.ImageField(upload_to="church_banners/", default="default/banner.jpg", blank=True, null=True, validators=[validate_image_file], help_text=_('Formato de arquivo: jpg, jpeg ou png.'))
   
    class Meta:
        verbose_name = "Igreja"
        verbose_name_plural = "Igrejas"

    def __str__(self):
        return self.user.get_full_name()
    
    def validate_cnpj(value: str) -> None:
        if value and not CNPJ().validate(value):
            raise ValidationError(_('CNPJ inválido.'), code='cnpj_invalido')


    def save(self, *args, **kwargs):      
        if not self.banner:
                self.banner.name = self._meta.get_field("banner").default
        super().save(*args, **kwargs)


class ChurchAddress(BaseAddress):
    church = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='addresses')
    def save(self, *args, **kwargs):
        if self.principal:
            ChurchAddress.objects.filter(church=self.church, principal=True).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)
    
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="member")
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    date_of_birth = models.DateField(_('Data de nascimento'), null=True, blank=True, help_text=_('Formato: DD/MM/AAAA.'))
    church = models.ForeignKey(Church, on_delete=models.PROTECT, null=True, blank=True, related_name='members')

    def validate_cpf(value: str) -> None:
        if value and not CPF(repeated_digits=True).validate(value):
            raise ValidationError(_('CPF inválido.'), code='cpf_invalido')

    def clean(self):        
        if self.date_of_birth and self.date_of_birth > timezone.localdate():
            raise ValidationError({'date_of_birth': 'Data de nascimento não pode ser maior que a data atual.'})

    class Meta:
        verbose_name = "Membro"
        verbose_name_plural = "Membros"

class MemberAddress(BaseAddress):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='addresses')

    def save(self, *args, **kwargs):
        if self.principal:
            MemberAddress.objects.filter(member=self.member, principal=True).exclude(pk=self.pk).update(principal=False)
        super().save(*args, **kwargs)
    
