import uuid
from datetime import datetime
from typing import Optional
from ninja import Schema, Field, UploadedFile
from pydantic import field_validator, model_validator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from dizimus.apps.users.models import User
from enum import Enum


# ─────────────────────────────────────────────────────────────────────────────
# Role — valores técnicos e labels amigáveis
# ─────────────────────────────────────────────────────────────────────────────

LABEL_TO_VALUE = {
    "Membro": "member",
    "Igreja": "church",
}
VALUE_TO_LABEL = {v: k for k, v in LABEL_TO_VALUE.items()}


class UserRoleEnum(str, Enum):
    MEMBER = "member"
    CHURCH = "church"


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

class RegisterIn(Schema):
    """Payload de cadastro. Role deve ser 'church' ou 'member'."""
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=8)
    password2: str = Field(..., min_length=8)
    user_label: str = "Membro"   # front envia label amigável
    phone: Optional[str] = None

    @field_validator("user_label")
    @classmethod
    def label_to_value(cls, v: str) -> str:
        if v not in LABEL_TO_VALUE:
            raise ValueError("Tipo de usuário inválido.")
        return LABEL_TO_VALUE[v]

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


class LoginIn(Schema):
    email: str
    password: str


class TokenOut(Schema):
    access: str
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
    uid: str
    token: str
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
    id: uuid.UUID
    email: str
    role: UserRoleEnum
    photo_url: str
    phone: Optional[str]
    slug: str
    is_trusty: bool
    date_joined: datetime
    created_at: datetime
    user_label: str

    @staticmethod
    def resolve_photo_url(obj: User) -> str:
        return obj.photo_url

    @staticmethod
    def resolve_phone(obj: User) -> Optional[str]:
        return str(obj.phone) if obj.phone else None

    @classmethod
    def from_orm(cls, user: User) -> "UserOut":
        return cls(
            id=user.id,
            email=user.email,
            role=user.role,
            photo_url=user.photo_url,
            phone=str(user.phone) if user.phone else None,
            slug=user.slug,
            is_trusty=user.is_trusty,
            date_joined=user.date_joined,
            created_at=user.created_at,
            user_label=VALUE_TO_LABEL[user.role],
        )


class UserUpdateIn(Schema):
    """Atualização parcial do perfil. Todos os campos são opcionais."""
    phone: Optional[str] = None
    photo: Optional[UploadedFile] = None


# ─────────────────────────────────────────────────────────────────────────────
# Mensagem genérica
# ─────────────────────────────────────────────────────────────────────────────

class MessageOut(Schema):
    detail: str
