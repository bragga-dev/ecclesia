# profile_church_schema.py
import uuid
from typing import Optional
from ninja import Schema
from dizimus.apps.users.models.user import User
from dizimus.apps.users.models.church import Church
from dizimus.apps.users.schemas.users_schemas import VALUE_TO_LABEL
from dizimus.apps.users.schemas.church_schemas import VALUE_TO_LABEL as CHURCH_VALUE_TO_LABEL


class ChurchProfileOut(Schema):
    # User base
    id:         uuid.UUID
    email:      str
    phone:      Optional[str]
    photo_url:  str
    slug:       str
    role:       str
    user_label: str

    # Church específico
    full_name:     Optional[str]
    cnpj:          Optional[str]
    instagram:     Optional[str]
    website:       Optional[str]
    about:         Optional[str]
    church_label:  str
    total_members: Optional[int]
    is_verified:   bool
    banner_url:    str

    @classmethod
    def from_orm(cls, user: User, church: Church) -> "ChurchProfileOut":
        return cls(
            id=user.id,
            email=user.email,
            phone=str(user.phone) if user.phone else None,
            photo_url=user.photo_url,
            slug=user.slug,
            role=user.role,
            user_label=VALUE_TO_LABEL[user.role],
            full_name=church.full_name,
            cnpj=church.cnpj,
            instagram=church.instagram,
            website=church.website,
            about=church.about,
            church_label=CHURCH_VALUE_TO_LABEL.get(church.church_type, church.church_type),
            total_members=church.total_members,
            is_verified=church.is_verified,
            banner_url=church.banner_url,
        )