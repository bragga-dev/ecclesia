# profile_member_schema.py
import uuid
from datetime import date
from typing import Optional
from ninja import Schema
from dizimus.apps.users.models.user import User
from dizimus.apps.users.models.member import Member
from dizimus.apps.users.schemas.users_schemas import VALUE_TO_LABEL
from dizimus.apps.users.schemas.member_schemas import VALUE_TO_LABEL as MEMBER_VALUE_TO_LABEL


class MemberProfileOut(Schema):
    # User base
    id:         uuid.UUID
    email:      str
    photo_url:  str
    role:       str
    user_label: str

    # Member específico
    username:           Optional[str]
    first_name:         Optional[str]
    last_name:          Optional[str]
    slug:               Optional[str]
    cpf:                Optional[str]
    phone:              Optional[str]
    date_of_birth:      Optional[date]
    contribution_label: str

    @classmethod
    def from_orm(cls, user: User, member: Member) -> "MemberProfileOut":
        return cls(
            id=user.id,
            email=user.email,
            photo_url=user.photo_url,
            slug=member.slug,
            role=user.role,
            user_label=VALUE_TO_LABEL[user.role],
            username=member.username,
            first_name=member.first_name,
            last_name=member.last_name,
            cpf=member.cpf,
            phone=str(member.phone) if member.phone else None,
            date_of_birth=member.date_of_birth,
            contribution_label=MEMBER_VALUE_TO_LABEL.get(member.contribution_type, member.contribution_type),
        )