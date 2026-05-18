import uuid
from datetime import datetime
from typing import Optional
from ninja import Schema, Field
from ninja import UploadedFile
from pydantic import field_validator, model_validator
from validate_docbr import CPF, CNPJ
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from dizimus.apps.users.models import User

_cpf  = CPF()
_cnpj = CNPJ()


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

class RegisterIn(Schema):
    """Payload de cadastro. Role deve ser 'church' ou 'member'."""
    username:   str = Field(..., min_length=3, max_length=15)
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name:  Optional[str] = Field(None, max_length=100)
    email:      str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password:   str = Field(..., min_length=8)
    password2:  str = Field(..., min_length=8)
    role:       User.UserRole = User.UserRole.MEMBER
    phone:      Optional[str] = None

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str) -> str:
        import re
        if not re.match(r'^[\w.@+-]+$', v):
            raise ValueError("Username inválido. Use apenas letras, números e @/./+/-/_.")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        try:
            validate_password(v)
        except DjangoValidationError as e:
            raise ValueError(", ".join(e.messages))
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterIn":
        if self.password != self.password2:
            raise ValueError("As senhas não coincidem.")
        return self
    
    @model_validator(mode="after")
    def validate_role_fields(self) -> "RegisterIn":
        if self.role == User.UserRole.MEMBER and not self.last_name:
            raise ValueError("Sobrenome é obrigatório para membros.")
        return self



class LoginIn(Schema):
    email:    str
    password: str


class TokenOut(Schema):
    access:  str
    refresh: str


class RefreshIn(Schema):
    refresh: str


class ChangePasswordIn(Schema):
    old_password: str
    new_password: str = Field(..., min_length=8)
    new_password2: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        try:
            validate_password(v)
        except DjangoValidationError as e:
            raise ValueError(", ".join(e.messages))
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordIn":
        if self.new_password != self.new_password2:
            raise ValueError("As senhas não coincidem.")
        return self


class PasswordResetRequestIn(Schema):
    email: str


class PasswordResetConfirmIn(Schema):
    token:        str
    new_password: str = Field(..., min_length=8)
    new_password2: str

    @model_validator(mode="after")
    def passwords_match(self) -> "PasswordResetConfirmIn":
        if self.new_password != self.new_password2:
            raise ValueError("As senhas não coincidem.")
        return self


# ─────────────────────────────────────────────────────────────────────────────
# User
# ─────────────────────────────────────────────────────────────────────────────

class UserOut(Schema):
    id:         uuid.UUID
    username:   str
    first_name: str
    last_name:  str
    email:      str
    role:       str
    photo_url:  str          # property do model — URL pública no MinIO
    phone:      Optional[str]
    slug:       str
    is_trusty:  bool
    date_joined: datetime
    created_at: datetime

    @staticmethod
    def resolve_photo_url(obj: User) -> str:
        return obj.photo_url  # usa a property com fallback seguro

    @staticmethod
    def resolve_phone(obj: User) -> Optional[str]:
        return str(obj.phone) if obj.phone else None


class UserUpdateIn(Schema):
    """Atualização parcial do perfil. Todos os campos são opcionais."""
    first_name: Optional[str] = Field(None, min_length=2, max_length=100)
    last_name:  Optional[str] = Field(None, min_length=2, max_length=100)
    username:   Optional[str] = Field(None, min_length=3, max_length=100)
    phone:      Optional[str] = None
    


# ─────────────────────────────────────────────────────────────────────────────
# Endereço (base — reutilizado por Church e Member)
# ─────────────────────────────────────────────────────────────────────────────

class AddressIn(Schema):
    cep:        str = Field(..., pattern=r'^\d{5}-\d{3}$', description="Formato: 00000-000")
    road:       str = Field(..., max_length=255)
    number:     str = Field(..., max_length=10)
    district:   str = Field(..., max_length=100)
    city:       str = Field(..., max_length=100)
    state:      str = Field(..., min_length=2, max_length=2)
    complement: Optional[str] = Field(None, max_length=255)
    principal:  bool = True


class AddressOut(Schema):
    id:         uuid.UUID
    cep:        str
    road:       str
    number:     str
    district:   str
    city:       str
    state:      str
    country:    str
    complement: Optional[str]
    principal:  bool
    slug:       str


# ─────────────────────────────────────────────────────────────────────────────
# Mensagem genérica (respostas simples)
# ─────────────────────────────────────────────────────────────────────────────

class MessageOut(Schema):
    detail: str