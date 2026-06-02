"""
Address Repository — persistência de endereços (Church e Member).
"""
import uuid
from typing import Optional

from dizimus.apps.users.models.church import Church, ChurchAddress
from dizimus.apps.users.models.member import  Member, MemberAddress


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