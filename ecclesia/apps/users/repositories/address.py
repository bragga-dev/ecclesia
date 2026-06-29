"""
Address Repository — persistência de endereços (Church e Member).
"""
import uuid
from typing import Optional

from ecclesia.apps.users.models.church import Church, ChurchAddress
from ecclesia.apps.users.models.member import  Member, MemberAddress


# ── Church addresses ──────────────────────────────────────────────────────────

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