import uuid
from datetime import date
from typing import Optional
from ninja import Schema, Field
from pydantic import field_validator
from validate_docbr import CPF
from dizimus.apps.users.models.member import Member
from dizimus.apps.users.schemas.addresses_schemas import AddressIn, AddressOut, AddressUpdateIn
from dizimus.apps.users.schemas.users_schemas import UserOut
from enum import Enum

_cpf = CPF()


LABEL_TO_VALUE = {
    "Nenhum": "none",
    "Dizimista": "dizimista",
    "Ofertante": "ofertante",
    "Dizimista e Ofertante": "both",
}
VALUE_TO_LABEL = {v: k for k, v in LABEL_TO_VALUE.items()}


class ContributionTypeEnum(str, Enum):
    NONE = "none"
    DIZIMISTA = "dizimista"
    OFERTANTE = "ofertante"
    BOTH = "both"


class MemberOut(Schema):
    id: uuid.UUID
    user: UserOut
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    cpf: Optional[str]
    phone: Optional[str]
    date_of_birth: Optional[date]
    contribution_type: ContributionTypeEnum
    contribution_label: str


    @classmethod
    def from_orm(cls, member: Member) -> "MemberOut":
        return cls(
            id=member.id,
            user=UserOut.from_orm(member.user),
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name,
            cpf=member.cpf,
            phone=str(member.phone) if member.phone else None,
            date_of_birth=member.date_of_birth,
            contribution_type=member.contribution_type,
            contribution_label=VALUE_TO_LABEL[member.contribution_type],
        )


class MemberCreateIn(Schema):
    user_id: uuid.UUID
    username: str = Field(..., min_length=3, max_length=30)
    first_name: str = Field(..., min_length=2, max_length=150)
    last_name: str = Field(..., min_length=2, max_length=150)
    cpf: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    contribution_label: str = Field(..., description="Tipo de contribuição: 'Nenhum', 'Dizimista', 'Ofertante' ou 'Dizimista e Ofertante'.")

    @field_validator("cpf")
    @classmethod
    def cpf_valid(cls, v: Optional[str]) -> Optional[str]:
        if v and not _cpf.validate(v):
            raise ValueError("CPF inválido.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def birth_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("Data de nascimento não pode ser no futuro.")
        return v

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str) -> str:
        import re
        if not re.match(r'^[\w.@+-]+$', v):
            raise ValueError("Username inválido. Use apenas letras, números e @/./+/-/_.")
        return v

    @field_validator("contribution_label")
    @classmethod
    def label_to_value(cls, v: str) -> str:
        if v not in LABEL_TO_VALUE:
            raise ValueError("Tipo de contribuição inválido.")
        return LABEL_TO_VALUE[v]

class MemberUpdateIn(Schema):
    username:   Optional[str] = Field(None, min_length=3, max_length=30)
    first_name: Optional[str] = Field(None, min_length=2, max_length=150)
    last_name:  Optional[str] = Field(None, min_length=2, max_length=150)
    cpf:        Optional[str] = None
    phone:      Optional[str] = None
    date_of_birth: Optional[date] = None
    contribution_label: Optional[str] = Field(None, description="Tipo de contribuição: 'Nenhum', 'Dizimista', 'Ofertante' ou 'Dizimista e Ofertante'.")

    
    @field_validator("cpf")
    @classmethod
    def cpf_valid(cls, v: Optional[str]) -> Optional[str]:
        if v and not _cpf.validate(v):
            raise ValueError("CPF inválido.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def birth_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("Data de nascimento não pode ser no futuro.")
        return v

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str) -> str:
        import re
        if not re.match(r'^[\w.@+-]+$', v):
            raise ValueError("Username inválido. Use apenas letras, números e @/./+/-/_.")
        return v
    
    @field_validator("contribution_label")
    @classmethod
    def label_to_value(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in LABEL_TO_VALUE:
            raise ValueError("Tipo de contribuição inválido.")
        return LABEL_TO_VALUE[v] if v else None


class MemberAddressIn(AddressIn):
    """Endereço de Membro — igual ao base."""
    pass

class MemberAddressUpdateIn(AddressUpdateIn):
    """Atualização parcial de endereço de Membro — igual ao base."""
    pass

class MemberAddressOut(AddressOut):
    member_id: uuid.UUID


__all__ = [
    "MemberOut",
    "MemberCreateIn",
    "MemberUpdateIn",
    "MemberAddressIn",
    "MemberAddressOut",
    "ContributionTypeEnum",
    "MemberAddressUpdateIn"
]



# ── Cadastro de membro por Igreja ─────────────────────────────────────────────

class ChurchRegisterMemberIn(Schema):
    """Payload para Igreja cadastrar um membro."""
    email:      str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    first_name: str = Field(..., min_length=2, max_length=150)
    last_name:  str = Field(..., min_length=2, max_length=150)


class MemberInviteOut(Schema):
    """Resposta após Igreja cadastrar um membro."""
    id:    uuid.UUID
    email: str
    first_name: Optional[str]
    last_name:  Optional[str]