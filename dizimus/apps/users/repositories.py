"""
Repositories — escrita no banco.
Toda persistência de User passa por aqui.
"""
import uuid
from typing import Optional
from django.core.files.uploadedfile import InMemoryUploadedFile

from dizimus.apps.users.models import User, Church, Member


def create_user(
    *,
    email: str,
    password: str,
    username: str,
    first_name: str,
    last_name: str,
    role: str,
    phone: Optional[str] = None,
) -> User:
    user = User.objects.create_user(
        email=email,
        password=password,
        username=username,
        first_name=first_name,
        last_name=last_name,
        role=role,
        phone=phone,
    )
    return user


def create_church_profile(user: User) -> Church:
    return Church.objects.create(user=user)


def create_member_profile(user: User) -> Member:
    return Member.objects.create(user=user)


def update_user(user: User, **fields) -> User:
    for attr, value in fields.items():
        if value is not None:
            setattr(user, attr, value)
    user.save()
    return user


def set_user_photo(user: User, photo: InMemoryUploadedFile) -> User:
    # Remove arquivo antigo do MinIO antes de substituir
    if user.photo and user.photo.name != "default/user_img.jpg":
        user.photo.delete(save=False)
    user.photo = photo
    user.save(update_fields=["photo"])
    return user


def remove_user_photo(user: User) -> User:
    if user.photo and user.photo.name != "default/user_img.jpg":
        user.photo.delete(save=False)
    user.photo = "default/user_img.jpg"
    user.save(update_fields=["photo"])
    return user


def activate_user(user: User) -> User:
    user.is_active = True
    user.is_trusty = True
    user.save(update_fields=["is_active", "is_trusty"])
    return user

"""
Adições ao repositories.py existente.
Cole estas funções no final do arquivo dizimus/apps/users/repositories.py
"""
import uuid
from typing import Optional

from dizimus.apps.users.models import (
    User, Church, Member,
    ChurchAddress, MemberAddress,
)


# ── Church profile ────────────────────────────────────────────────────────────

def update_church_profile(church: Church, **fields) -> Church:
    for attr, value in fields.items():
        setattr(church, attr, value)
    church.save()
    return church


def set_church_banner(church: Church, banner) -> Church:
    if church.banner and church.banner.name != "default/banner.jpg":
        church.banner.delete(save=False)
    church.banner = banner
    church.save(update_fields=["banner"])
    return church


def remove_church_banner(church: Church) -> Church:
    if church.banner and church.banner.name != "default/banner.jpg":
        church.banner.delete(save=False)
    church.banner = "default/banner.jpg"
    church.save(update_fields=["banner"])
    return church


# ── Member profile ────────────────────────────────────────────────────────────

def update_member_profile(member: Member, **fields) -> Member:
    for attr, value in fields.items():
        setattr(member, attr, value)
    member.full_clean()   # dispara validação do model (data_of_birth no futuro, etc.)
    member.save()
    return member


# ── Church addresses ──────────────────────────────────────────────────────────

def get_church_addresses(church: Church):
    return church.addresses.all().order_by("-principal", "road")


def get_church_address_by_id(church: Church, address_id: uuid.UUID) -> Optional[ChurchAddress]:
    return church.addresses.filter(pk=address_id).first()


def create_church_address(church: Church, **fields) -> ChurchAddress:
    address = ChurchAddress(church=church, **fields)
    address.full_clean()
    address.save()
    return address


def update_church_address(address: ChurchAddress, **fields) -> ChurchAddress:
    for attr, value in fields.items():
        if value is not None:
            setattr(address, attr, value)
    address.full_clean()
    address.save()
    return address


def delete_church_address(address: ChurchAddress) -> None:
    address.delete()


# ── Member addresses ──────────────────────────────────────────────────────────

def get_member_addresses(member: Member):
    return member.addresses.all().order_by("-principal", "road")


def get_member_address_by_id(member: Member, address_id: uuid.UUID) -> Optional[MemberAddress]:
    return member.addresses.filter(pk=address_id).first()


def create_member_address(member: Member, **fields) -> MemberAddress:
    address = MemberAddress(member=member, **fields)
    address.full_clean()
    address.save()
    return address


def update_member_address(address: MemberAddress, **fields) -> MemberAddress:
    for attr, value in fields.items():
        if value is not None:
            setattr(address, attr, value)
    address.full_clean()
    address.save()
    return address


def delete_member_address(address: MemberAddress) -> None:
    address.delete()