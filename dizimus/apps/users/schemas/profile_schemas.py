"""
Schemas de perfil — Church, Member e Endereços.
Complementa users_schemas.py com os tipos específicos de cada role.
"""
from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from ninja import Schema
from pydantic import field_validator

from dizimus.apps.users.validators import validate_cpf, validate_cnpj
from django.core.exceptions import ValidationError as DjangoValidationError


# ── Church ────────────────────────────────────────────────────────────────────

class ChurchUpdateIn(Schema):
    """
    Campos editáveis do perfil Igreja.
    Todos opcionais — envie apenas o que deseja alterar.
    """
    cnpj:      Optional[str] = None
    instagram: Optional[str] = None
    website:   Optional[str] = None
    about:     Optional[str] = None

    @field_validator("cnpj")
    @classmethod
    def check_cnpj(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            validate_cnpj(v)
        except DjangoValidationError as e:
            raise ValueError(e.message) from e
        return v

    @field_validator("about")
    @classmethod
    def check_about_length(cls, v: str | None) -> str | None:
        if v and len(v) > 1000:
            raise ValueError("A descrição não pode ultrapassar 1000 caracteres.")
        return v


class ChurchProfileOut(Schema):
    cnpj:          Optional[str]
    instagram:     Optional[str]
    website:       Optional[str]
    about:         Optional[str]
    total_members: int
    is_verified:   bool
    banner_url:    str

    @staticmethod
    def resolve_banner_url(obj) -> str:
        return obj.banner_url  # property definida no model


# ── Member ────────────────────────────────────────────────────────────────────

class MemberUpdateIn(Schema):
    """
    Campos editáveis do perfil Membro.
    Todos opcionais — envie apenas o que deseja alterar.
    """
    cpf:           Optional[str]  = None
    date_of_birth: Optional[date] = None

    @field_validator("cpf")
    @classmethod
    def check_cpf(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            validate_cpf(v)
        except DjangoValidationError as e:
            raise ValueError(e.message) from e
        return v

    @field_validator("date_of_birth")
    @classmethod
    def check_date_of_birth(cls, v: date | None) -> date | None:
        if v is None:
            return v
        from django.utils import timezone
        if v > timezone.localdate():
            raise ValueError("Data de nascimento não pode ser no futuro.")
        return v


class MemberProfileOut(Schema):
    cpf:           Optional[str]
    date_of_birth: Optional[date]


# ── Address ───────────────────────────────────────────────────────────────────

class AddressIn(Schema):
    """Payload para criar um endereço (Church ou Member)."""
    cep:        str
    road:       str
    number:     str
    district:   str
    city:       str
    state:      str
    country:    str            = "Brasil"
    complement: Optional[str] = None
    principal:  bool           = True

    @field_validator("cep")
    @classmethod
    def check_cep(cls, v: str) -> str:
        from dizimus.apps.users.validators import validar_cep
        try:
            validar_cep(v)
        except DjangoValidationError as e:
            raise ValueError(e.message) from e
        return v

    @field_validator("state")
    @classmethod
    def check_state(cls, v: str) -> str:
        from dizimus.apps.users.models import BaseAddress
        valid = [s.value for s in BaseAddress.States]
        if v.upper() not in valid:
            raise ValueError(f"Estado inválido. Use a sigla de 2 letras (ex: SP, BA).")
        return v.upper()


class AddressUpdateIn(Schema):
    """Payload para atualização parcial de endereço."""
    cep:        Optional[str]  = None
    road:       Optional[str]  = None
    number:     Optional[str]  = None
    district:   Optional[str]  = None
    city:       Optional[str]  = None
    state:      Optional[str]  = None
    country:    Optional[str]  = None
    complement: Optional[str]  = None
    principal:  Optional[bool] = None

    @field_validator("cep")
    @classmethod
    def check_cep(cls, v: str | None) -> str | None:
        if v is None:
            return v
        from dizimus.apps.users.validators import validar_cep
        try:
            validar_cep(v)
        except DjangoValidationError as e:
            raise ValueError(e.message) from e
        return v

    @field_validator("state")
    @classmethod
    def check_state(cls, v: str | None) -> str | None:
        if v is None:
            return v
        from dizimus.apps.users.models import BaseAddress
        valid = [s.value for s in BaseAddress.States]
        if v.upper() not in valid:
            raise ValueError("Estado inválido. Use a sigla de 2 letras (ex: SP, BA).")
        return v.upper()


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