# profile_church_schema.py
import uuid
from typing import Optional
from ninja import Schema

from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.models.church import Church
from ecclesia.apps.users.schemas.users_schemas import UserRoleEnum


class ChurchProfileOut(Schema):
    # User base
    id:          uuid.UUID
    email:       str
    photo_url:   Optional[str] = None
    role:        UserRoleEnum
    role_label:  str  

    # Church específico
    full_name:     Optional[str]
    cnpj:          Optional[str]
    instagram:     Optional[str]
    website:       Optional[str]
    about:         Optional[str]
    phone:         Optional[str]
    slug:          Optional[str]
    church_type_label:  Optional[str] = None  
    church_type:  Optional[str] = None  
    total_members: Optional[int]
    is_verified:   bool
    banner_url:    Optional[str] = None

    @classmethod
    def from_orm(cls, user: User, church: Church) -> "ChurchProfileOut":
        return cls(
            # User fields
            id=user.id,
            email=user.email,
            photo_url=getattr(user, "photo_url", None),
            role=user.role,
            role_label=user.get_role_display(),
            
            # Church fields
            full_name=church.full_name,
            cnpj=church.cnpj,
            instagram=church.instagram,
            website=church.website,
            about=church.about,
            phone=str(church.phone) if church.phone else None,
            slug=church.slug,
            church_type_label=church.get_church_type_display() if hasattr(church, 'get_church_type_display') else None,
            church_type=church.church_type,
            total_members=church.total_members,
            is_verified=church.is_verified,
            banner_url=getattr(church, "banner_url", None),
        )


