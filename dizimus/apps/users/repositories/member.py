"""
Member Repository — persistência de perfil Membro.
"""
from dizimus.apps.users.models.user import User
from dizimus.apps.users.models.member import  Member
from typing import Optional


def create_member_profile(
    user: User,
    *,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None,
    cpf: Optional[str] = None,
    date_of_birth: Optional[str] = None,
) -> Member:
    return Member.objects.create(
        user=user,
        first_name=first_name,
        last_name=last_name,
        username=username,
        cpf=cpf,
        date_of_birth=date_of_birth,
    )


def update_member_profile(member: Member, **fields) -> Member:
    for attr, value in fields.items():
        if value is not None:
            setattr(member, attr, value)
    member.full_clean()   
    member.save()
    return member
