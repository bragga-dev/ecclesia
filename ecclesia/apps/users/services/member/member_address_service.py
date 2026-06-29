# member_address_service.py
"""
Member Address Service — CRUD de endereços exclusivo para Member.
"""
import uuid
from typing import Optional

from ecclesia.apps.users.models.member import Member, MemberAddress
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.repositories.address import (
    create_member_address,
    update_member_address,
    delete_member_address,
)
from ecclesia.apps.users.selectors.member_selector import (
    get_member_by_user_id,
    get_address_by_id_and_member,
    get_addresses_by_member,
    get_member_principal_address,
    get_member_address_by_id,
)
from ecclesia.apps.users.schemas.addresses_schemas import AddressIn, AddressUpdateIn


def _get_member(user: User) -> Optional[Member]:
    """Obtém o membro vinculado ao usuário."""
    return get_member_by_user_id(user.id)


def list_member_addresses(user: User):
    """
    Lista todos os endereços do membro do usuário logado.
    """
    member = _get_member(user)
    if not member:
        return MemberAddress.objects.none()
    return get_addresses_by_member(member.id)


def get_member_address_detail(user: User, address_id: uuid.UUID) -> Optional[MemberAddress]:
    """
    Busca um endereço específico do membro do usuário.
    """
    member = _get_member(user)
    if not member:
        return None
    return get_address_by_id_and_member(address_id, member.id)


def get_member_principal_address_service(user: User) -> Optional[MemberAddress]:
    """
    Retorna o endereço principal do membro do usuário.
    """
    member = _get_member(user)
    if not member:
        return None
    return get_member_principal_address(member.id)


def create_member_address_service(user: User, data: AddressIn) -> Optional[MemberAddress]:
    """
    Cria um novo endereço para o membro do usuário.
    Se for o primeiro endereço ou marcado como principal,
    remove o principal anterior.
    """
    member = _get_member(user)
    if not member:
        return None

    payload = data.model_dump()
    
    # Se este endereço for marcado como principal, remove o principal anterior
    if payload.get("principal", False):
        current_principal = get_member_principal_address(member.id)
        if current_principal:
            current_principal.principal = False
            current_principal.save(update_fields=["principal"])
    
    # Se não houver nenhum endereço, força como principal
    existing_addresses = get_addresses_by_member(member.id)
    if not existing_addresses.exists():
        payload["principal"] = True
    
    return create_member_address(member, **payload)


def update_member_address_service(
    user: User, 
    address_id: uuid.UUID, 
    data: AddressUpdateIn
) -> Optional[MemberAddress]:
    """
    Atualiza um endereço existente do membro do usuário.
    """
    member = _get_member(user)
    if not member:
        return None
    
    address = get_address_by_id_and_member(address_id, member.id)
    if not address:
        return None
    
    payload = data.model_dump(exclude_none=True)
    
    # Se estiver marcando como principal, remove o principal anterior
    if payload.get("principal") is True:
        current_principal = get_member_principal_address(member.id)
        if current_principal and current_principal.id != address_id:
            current_principal.principal = False
            current_principal.save(update_fields=["principal"])
    
    # Se estiver desmarcando como principal e era o único principal,
    # mantém como principal (não pode ficar sem endereço principal)
    if payload.get("principal") is False:
        principal_count = get_addresses_by_member(member.id).filter(principal=True).count()
        if principal_count == 1 and address.principal:
            payload["principal"] = True
    
    return update_member_address(address, **payload)


def delete_member_address_service(user: User, address_id: uuid.UUID) -> bool:
    """
    Deleta um endereço do membro do usuário.
    Retorna True se deletou, False se não encontrou ou é o único.
    """
    member = _get_member(user)
    if not member:
        return False
    
    address = get_address_by_id_and_member(address_id, member.id)
    if not address:
        return False
    
    # Verifica se é o único endereço
    address_count = get_addresses_by_member(member.id).count()
    if address_count == 1:
        # Não pode deletar o único endereço
        return False
    
    # Se o endereço deletado era principal, marca outro como principal
    was_principal = address.principal
    
    delete_member_address(address)
    
    if was_principal:
        new_principal = get_addresses_by_member(member.id).first()
        if new_principal:
            new_principal.principal = True
            new_principal.save(update_fields=["principal"])
    
    return True