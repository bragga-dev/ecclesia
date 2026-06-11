import uuid
from datetime import datetime
from typing import Optional
from ninja import Schema, Field
from ninja import UploadedFile
from pydantic import field_validator, model_validator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from dizimus.apps.users.models.user import User

from enum import Enum



# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────


LABEL_TO_VALUE = {
    "Membro": "member",
    "Igreja": "church",
}
VALUE_TO_LABEL = {v: k for k, v in LABEL_TO_VALUE.items()}


class UserRoleEnum(str, Enum):
    MEMBER = "member"
    CHURCH = "church"
    ADMIN =  "admin"

class RegisterIn(Schema):
    email:     str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password:  str = Field(..., min_length=8)
    password2: str = Field(..., min_length=8)
    user_label: str = "Membro" 

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
    uid:         str
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
    id:          uuid.UUID
    email:       str
    role:        UserRoleEnum
    photo_url:   str
    is_trusty:   bool
    is_active:   bool
    date_joined: datetime
    created_at:  datetime
    user_label:  str

    @staticmethod
    def resolve_photo_url(obj: User) -> str:
        return obj.photo_url

    @staticmethod
    def resolve_user_label(obj: User) -> str:  
        return VALUE_TO_LABEL.get(obj.role, obj.role)

# ─────────────────────────────────────────────────────────────────────────────
# Mensagem genérica (respostas simples)
# ─────────────────────────────────────────────────────────────────────────────

class MessageOut(Schema):
    detail: str