"""
Schemas Endereços.
Complementa users_schemas.py com os tipos específicos de cada role.
"""
from __future__ import annotations

import uuid
from typing import Optional
from ninja import Schema
from pydantic import field_validator
from django.core.exceptions import ValidationError as DjangoValidationError




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
        from dizimus.apps.users.validators.validate_cep import validar_cep
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
        from dizimus.apps.users.validators.validate_cpf_cnpj import validar_cep
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


__all__ = [
    "AddressIn",
    "AddressUpdateIn",
    "AddressOut",
]