import uuid
from datetime import datetime
from typing import Optional

from ninja import Schema, Field
from pydantic import EmailStr

from dizimus.apps.community.models.member_church_model import MemberChurch
from dizimus.apps.users.schemas.member_schemas import MemberOut
from dizimus.apps.users.schemas.church_schemas import ChurchOut


# ── Saída completa do vínculo ─────────────────────────────────────────────────

class MemberChurchOut(Schema):
    id:                uuid.UUID
    member:            MemberOut
    church:            ChurchOut
    joined_at:         datetime
    role:              MemberChurch.Role
    status:            MemberChurch.Status
    contribution_type: MemberChurch.ContributionType
    role_label:        str
    status_label:      str
    contribution_label: str

    @classmethod
    def from_orm(cls, member_church: MemberChurch) -> "MemberChurchOut":
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



# ── Atualização de vínculo ────────────────────────────────────────────────────

class MemberChurchUpdateIn(Schema):
    role:              Optional[MemberChurch.Role]             = None
    status:            Optional[MemberChurch.Status]           = None
    contribution_type: Optional[MemberChurch.ContributionType] = None


# ── Igreja cadastra membro ────────────────────────────────────────────────────

class ChurchRegisterMemberIn(Schema):
    email:             EmailStr
    first_name:        str = Field(..., min_length=2, max_length=150)
    last_name:         str = Field(..., min_length=2, max_length=150)
    role: MemberChurch.Role = MemberChurch.Role.MEMBER
    status: MemberChurch.Status = MemberChurch.Status.ACTIVE
    contribution_type: MemberChurch.ContributionType = MemberChurch.ContributionType.NONE


class MemberInviteOut(Schema):
    id:         uuid.UUID
    email:      str
    first_name: Optional[str]
    last_name:  Optional[str]
    


# ── Listagem de membros pela Igreja ──────────────────────────────────────────

class ChurchMemberListOut(Schema):
    member:            MemberOut
    role:              MemberChurch.Role
    status:            MemberChurch.Status
    contribution_type: MemberChurch.ContributionType
    joined_at:         datetime
    left_at:           Optional[datetime]

    @classmethod
    def from_membership(cls, membership) -> "ChurchMemberListOut":
        return cls(
            member=MemberOut.from_orm(membership.member),
            role=membership.role,
            status=membership.status,
            contribution_type=membership.contribution_type,
            joined_at=membership.joined_at,
            left_at=membership.left_at,
        )


__all__ = [
    "MemberChurchOut",
    "MemberChurchUpdateIn",
    "ChurchRegisterMemberIn",
    "MemberInviteOut",
    "ChurchMemberListOut",
]