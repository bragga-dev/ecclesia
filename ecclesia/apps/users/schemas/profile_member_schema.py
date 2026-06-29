# profile_member_schema.py
import uuid
from datetime import date
from typing import Optional
from ninja import Schema

from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.models.member import Member
from ecclesia.apps.users.schemas.users_schemas import UserRoleEnum


class MemberProfileOut(Schema):
    # User base
    id:         uuid.UUID
    email:      str
    photo_url:  str
    role:       UserRoleEnum
    role_label: str  # Mudado de user_label para role_label (padrão)

    # Member específico
    username:           Optional[str]
    first_name:         Optional[str]
    last_name:          Optional[str]
    slug:               Optional[str]
    cpf:                Optional[str]
    phone:              Optional[str]
    date_of_birth:      Optional[date]
    contribution_label: Optional[str]  # Adicionei Optional

    @classmethod
    def from_orm(cls, user: User, member: Member) -> "MemberProfileOut":
        return cls(
            # User fields
            id=user.id,
            email=user.email,
            photo_url=user.photo_url,
            role=user.role,
            role_label=user.get_role_display(),  # Usa o método do model
            
            # Member fields
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name,
            slug=member.slug,
            cpf=member.cpf,
            phone=str(member.phone) if member.phone else None,
            date_of_birth=member.date_of_birth,
            contribution_label=member.get_contribution_type_display() if hasattr(member, 'get_contribution_type_display') else None,
        )