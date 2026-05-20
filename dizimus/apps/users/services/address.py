"""
Address Services — CRUD de endereços para Church e Member.
"""
import uuid

from dizimus.apps.users.models import User
from dizimus.apps.users import repositories
from dizimus.apps.users.schemas.profile_schemas import AddressIn, AddressUpdateIn


def _get_church(user: User):
    church, _ = user.church_set.get_or_create(user=user)
    return church


def _get_member(user: User):
    member, _ = user.member_set.get_or_create(user=user)
    return member


def list_my_addresses(user: User):
    if user.role == User.UserRole.CHURCH:
        return repositories.get_church_addresses(_get_church(user))
    return repositories.get_member_addresses(_get_member(user))


def create_my_address(user: User, data: AddressIn):
    payload = data.model_dump()
    if user.role == User.UserRole.CHURCH:
        return repositories.create_church_address(_get_church(user), **payload)
    return repositories.create_member_address(_get_member(user), **payload)


def update_my_address(user: User, address_id: uuid.UUID, data: AddressUpdateIn):
    payload = data.model_dump(exclude_none=True)

    if user.role == User.UserRole.CHURCH:
        address = repositories.get_church_address_by_id(_get_church(user), address_id)
        if not address:
            return None
        return repositories.update_church_address(address, **payload)

    address = repositories.get_member_address_by_id(_get_member(user), address_id)
    if not address:
        return None
    return repositories.update_member_address(address, **payload)


def delete_my_address(user: User, address_id: uuid.UUID) -> bool:
    """Retorna True se deletou, False se não encontrou."""
    if user.role == User.UserRole.CHURCH:
        address = repositories.get_church_address_by_id(_get_church(user), address_id)
        if not address:
            return False
        repositories.delete_church_address(address)
        return True

    address = repositories.get_member_address_by_id(_get_member(user), address_id)
    if not address:
        return False
    repositories.delete_member_address(address)
    return True