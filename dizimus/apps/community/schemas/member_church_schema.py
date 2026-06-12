import uuid
from datetime import date, datetime
from typing import Optional
from ninja import Schema, Field
from pydantic import field_validator
from dizimus.apps.community.models.member_church_model import MemberChurch
from dizimus.apps.users.schemas.member_schemas import MemberOut
from dizimus.apps.users.schemas.church_schemas import ChurchOut
from enum import Enum
from pydantic import EmailStr

class MemberChurchRoleEnum(str, Enum):
    MEMBER       = "member"
    PASTOR       = "pastor/padre"
    TREASURER    = "tesoureiro"
    SECRETARY    = "secretário"  
    CHURCH_ADMIN = "admin"   

class MemberChurchStatusEnum(str, Enum):
    ACTIVE   = "active"
    INACTIVE = "inactive"
    PENDING  = "pending" 

class MemberChurchContributionTypeEnum(str, Enum):
    NONE = "none"
    DIZIMISTA = "dizimista"
    OFERTANTE = "ofertante"
    BOTH = "both"



class MemberChurchOut(Schema):
    id: uuid.UUID
    member: MemberOut
    church: ChurchOut
    joined_at: datetime
    
    role: MemberChurchRoleEnum
    status: MemberChurchStatusEnum
    contribution_type: MemberChurchContributionTypeEnum

    role_label: str
    status_label: str
    contribution_label: str

    @classmethod
    def from_orm(cls, member_church: MemberChurch):
        return cls(
            id=member_church.id,
            member=MemberOut.from_orm(member_church.member),
            church=ChurchOut.from_orm(member_church.church),
            joined_at=member_church.joined_at,

            role=member_church.role,
            status=member_church.status,
            contribution_type=member_church.contribution_type,

            role_label=member_church.get_role_display(),
            status_label=member_church.get_status_display(),
            contribution_label=member_church.get_contribution_type_display(),
        )
class MemberChurchCreateIn(Schema):
    member_id: uuid.UUID
    church_id: uuid.UUID

    role:MemberChurchRoleEnum = MemberChurchRoleEnum.MEMBER
    status: MemberChurchStatusEnum = MemberChurchStatusEnum.PENDING
    contribution_type: MemberChurchContributionTypeEnum = MemberChurchContributionTypeEnum.NONE

    @field_validator("member_id")
    @classmethod
    def validate_member_id(cls, value):
        if not value:
            raise ValueError("O membro é obrigatório.")
        return value

    @field_validator("church_id")
    @classmethod
    def validate_church_id(cls, value):
        if not value:
            raise ValueError("A igreja é obrigatória.")
        return value

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        allowed = {choice[0] for choice in MemberChurch.Role.choices}

        if value not in allowed:
            raise ValueError("Função inválida.")

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        allowed = {choice[0] for choice in MemberChurch.Status.choices}

        if value not in allowed:
            raise ValueError("Status inválido.")

        return value

    @field_validator("contribution_type")
    @classmethod
    def validate_contribution_type(cls, value):
        allowed = {
            choice[0]
            for choice in MemberChurch.ContributionType.choices
        }

        if value not in allowed:
            raise ValueError(
                "Tipo de contribuição inválido."
            )

        return value

class MemberChurchUpdateIn(Schema):
    role: Optional[MemberChurchRoleEnum] = None
    status: Optional[MemberChurchStatusEnum] = None
    contribution_type: Optional[MemberChurchContributionTypeEnum] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        if value is None:
            return value

        allowed = {choice[0] for choice in MemberChurch.Role.choices}

        if value not in allowed:
            raise ValueError("Função inválida.")

        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value is None:
            return value

        allowed = {choice[0] for choice in MemberChurch.Status.choices}

        if value not in allowed:
            raise ValueError("Status inválido.")

        return value

    @field_validator("contribution_type")
    @classmethod
    def validate_contribution_type(cls, value):
        if value is None:
            return value

        allowed = {
            choice[0]
            for choice in MemberChurch.ContributionType.choices
        }

        if value not in allowed:
            raise ValueError(
                "Tipo de contribuição inválido."
            )

        return value
    

# ── Cadastro de membro por Igreja ─────────────────────────────────────────────

class ChurchRegisterMemberIn(Schema):
    """Payload para Igreja cadastrar um membro."""
    email:      EmailStr
    first_name: str = Field(..., min_length=2, max_length=150)
    last_name:  str = Field(..., min_length=2, max_length=150)
    contribution_type: MemberChurchContributionTypeEnum = MemberChurchContributionTypeEnum.NONE
    


class MemberInviteOut(Schema):
    """Resposta após Igreja cadastrar um membro."""
    id:    uuid.UUID
    email: str
    first_name: Optional[str]
    last_name:  Optional[str]


# ── Listagem de membros pela Igreja ──────────────────────────────────────────
class ChurchMemberListOut(Schema):
    member: MemberOut

    role: MemberChurchRoleEnum
    status: MemberChurchStatusEnum
    contribution_type: MemberChurchContributionTypeEnum

    joined_at: datetime
    left_at: Optional[datetime]

    @classmethod
    def from_membership(cls, membership):

        return cls(
            member=MemberOut.from_orm(
                membership.member
            ),

            role=membership.role,
            status=membership.status,
            contribution_type=membership.contribution_type,

            joined_at=membership.joined_at,
            left_at=membership.left_at,
        )

__all__ = [
    "MemberChurchOut",
    "MemberChurchCreateIn",
    "MemberChurchUpdateIn",
    "ChurchRegisterMemberIn",
    "MemberInviteOut",
    "ChurchMemberListOut",
]