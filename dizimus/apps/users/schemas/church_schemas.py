# church_schemas.py
import uuid
from typing import Optional
from ninja import Schema, Field
from validate_docbr import CNPJ
from pydantic import field_validator
from enum import Enum

from dizimus.apps.users.schemas.addresses_schemas import AddressIn, AddressOut, AddressUpdateIn
from dizimus.apps.users.models.church import Church
from dizimus.apps.users.schemas.users_schemas import UserOut

_cnpj = CNPJ()


# ── Enums ─────────────────────────────────────────────────────────────────────

class ChurchTypeEnum(str, Enum):
    HEADQUARTERS = "headquarters"
    COMMUNITY = "community"
    INDEPENDENT = "independent"


# ── Saída (GET /churches) ────────────────────────────────────────────────────

class ChurchOut(Schema):
    id: uuid.UUID
    user: UserOut
    is_verified: bool
    is_active: bool
    cnpj: Optional[str]
    banner_url: Optional[str]
    church_type: ChurchTypeEnum
    church_type_label: str  
    full_name: Optional[str]
    instagram: Optional[str]
    website: Optional[str]
    about: Optional[str]
    phone: Optional[str]
    total_members: Optional[int]
    parent_church_id: Optional[uuid.UUID]

    @classmethod
    def from_orm(cls, church: Church) -> "ChurchOut":
        return cls(
            id=church.id,
            user=UserOut.from_orm(church.user),
            is_verified=church.is_verified,
            is_active=church.user.is_active,
            cnpj=church.cnpj,
            banner_url=church.banner_url,
            church_type=church.church_type,
            church_type_label=church.get_church_type_display(), 
            full_name=church.full_name,
            instagram=church.instagram,
            website=church.website,
            about=church.about,
            phone=str(church.phone) if church.phone else None,
            total_members=church.total_members,
            parent_church_id=church.parent_church_id,
        )


# ── Entrada para criação (POST /churches) ────────────────────────────────────

class ChurchCreateIn(Schema):
    user_id: uuid.UUID
    full_name: str = Field(..., min_length=3, max_length=255)
    cnpj: Optional[str] = None
    church_type: ChurchTypeEnum = ChurchTypeEnum.INDEPENDENT  
    instagram: Optional[str] = None
    website: Optional[str] = None
    about: Optional[str] = None
    phone: Optional[str] = None
    parent_church_id: Optional[uuid.UUID] = None

    @field_validator("cnpj")
    @classmethod
    def cnpj_valid(cls, v: Optional[str]) -> Optional[str]:
        if v and not _cnpj.validate(v):
            raise ValueError("CNPJ inválido.")
        return v


# ── Entrada para atualização (PATCH/PUT /churches/{id}) ──────────────────────

class ChurchUpdateIn(Schema):
    cnpj: Optional[str] = None
    church_type: Optional[ChurchTypeEnum] = None  # Mudado de church_label para church_type
    full_name: Optional[str] = None
    instagram: Optional[str] = None
    website: Optional[str] = None
    about: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("cnpj")
    @classmethod
    def cnpj_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        if not _cnpj.validate(v):
            raise ValueError("CNPJ inválido.")
        return v

    # Removido o validador label_to_value pois agora usamos o Enum diretamente


# ── Endereços ────────────────────────────────────────────────────────────────

class ChurchAddressIn(AddressIn):
    """Endereço de Igreja — igual ao base."""
    pass


class ChurchAddressOut(AddressOut):
    church_id: uuid.UUID


class ChurchAddressUpdateIn(AddressUpdateIn):
    """Atualização parcial de endereço de Igreja — igual ao base."""
    pass


# ── re-export para facilitar importação nos routers ──────────────────────────

__all__ = [
    "ChurchOut",
    "ChurchCreateIn",
    "ChurchUpdateIn",
    "ChurchAddressIn",
    "ChurchAddressOut",
    "ChurchTypeEnum",
    "ChurchAddressUpdateIn"
]