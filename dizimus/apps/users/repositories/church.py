
"""
Church Repository — persistência de perfil Igreja.
"""
from dizimus.apps.users.models.user import User
from dizimus.apps.users.models.church import  Church
from typing import Optional
import uuid

def create_church_profile(
    user: User,
    *,
    full_name: Optional[str] = None,
    cnpj: Optional[str] = None,
    instagram: Optional[str] = None,
    website: Optional[str] = None,
    about: Optional[str] = None,
    
) -> Church:
    return Church.objects.create(
        user=user,
        full_name=full_name,
        cnpj=cnpj,
        instagram=instagram,
        website=website,
        about=about,
    )

def update_church_profile(church: Church, **fields) -> Church:
    for attr, value in fields.items():
        if value is not None:
            setattr(church, attr, value)
    church.full_clean()
    church.save()
    return church


def set_church_as_verified(church: Church) -> Church:
    if not church.is_verified:
        church.is_verified = True
        church.save(update_fields=["is_verified"])
    return church



def set_church_as_unverified(church: Church) -> Church:
    if  church.is_verified:
        church.is_verified = False
        church.save(update_fields=["is_verified"])
    return church
