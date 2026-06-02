
"""
Church Repository — persistência de perfil Igreja.
"""
from dizimus.apps.users.models.user import User
from dizimus.apps.users.models.church import  Church
from typing import Optional


def create_church_profile(
    user: User,
    *,
    full_name: str,
    cnpj: Optional[str] = None,
    instagram: Optional[str] = None,
    website: Optional[str] = None,
    about: Optional[str] = None,
    parent_church_id: Optional[str] = None,
    banner: Optional[str] = None,
) -> Church:
    return Church.objects.create(
        user=user,
        full_name=full_name,
        cnpj=cnpj,
        instagram=instagram,
        website=website,
        about=about,
        parent_church_id=parent_church_id,
        banner=banner,
    )

def update_church_profile(church: Church, **fields) -> Church:
    for attr, value in fields.items():
        if value is not None:
            setattr(church, attr, value)
    church.full_clean()
    church.save()
    return church
