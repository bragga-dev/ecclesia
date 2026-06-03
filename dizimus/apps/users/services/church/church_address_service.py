"""
Church Address Service — CRUD de endereços exclusivo para Church.
"""
import uuid
from typing import Optional

from dizimus.apps.users.models.church import Church, ChurchAddress
from dizimus.apps.users.models.user import User
from dizimus.apps.users.repositories.address import (
    create_church_address,
    update_church_address,
    delete_church_address,
)
from dizimus.apps.users.selectors.church_selector import (
    get_church_by_user_id,
    get_address_by_id_and_church,
    get_addresses_by_church,
    get_church_principal_address,
    
)
from dizimus.apps.users.schemas.addresses_schemas import AddressIn, AddressUpdateIn


def _get_church(user: User) -> Optional[Church]:
    """Obtém a igreja vinculada ao usuário."""
    return get_church_by_user_id(user.id)


def list_church_addresses(user: User):
    """
    Lista todos os endereços da igreja do usuário logado.
    """
    church = _get_church(user)
    if not church:
        return ChurchAddress.objects.none()
    return get_addresses_by_church(church.id)


def get_church_address_detail(user: User, address_id: uuid.UUID) -> Optional[ChurchAddress]:
    """
    Busca um endereço específico da igreja do usuário.
    """
    church = _get_church(user)
    if not church:
        return None
    return get_address_by_id_and_church(address_id, church.id)


def get_church_principal_address_service(user: User) -> Optional[ChurchAddress]:
    """
    Retorna o endereço principal da igreja do usuário.
    """
    church = _get_church(user)
    if not church:
        return None
    return get_church_principal_address(church.id)


def create_church_address_service(user: User, data: AddressIn) -> Optional[ChurchAddress]:
    """
    Cria um novo endereço para a igreja do usuário.
    Se for o primeiro endereço ou marcado como principal,
    remove o principal anterior.
    """
    church = _get_church(user)
    if not church:
        return None

    payload = data.model_dump()
    
    # Se este endereço for marcado como principal, remove o principal anterior
    if payload.get("principal", False):
        current_principal = get_church_principal_address(church.id)
        if current_principal:
            current_principal.principal = False
            current_principal.save(update_fields=["principal"])
    
    # Se não houver nenhum endereço, força como principal
    existing_addresses = get_addresses_by_church(church.id)
    if not existing_addresses.exists():
        payload["principal"] = True
    
    return create_church_address(church, **payload)


def update_church_address_service(
    user: User, 
    address_id: uuid.UUID, 
    data: AddressUpdateIn
) -> Optional[ChurchAddress]:
    """
    Atualiza um endereço existente da igreja do usuário.
    """
    church = _get_church(user)
    if not church:
        return None
    
    address = get_address_by_id_and_church(address_id, church.id)
    if not address:
        return None
    
    payload = data.model_dump(exclude_none=True)
    
    # Se estiver marcando como principal, remove o principal anterior
    if payload.get("principal") is True:
        current_principal = get_church_principal_address(church.id)
        if current_principal and current_principal.id != address_id:
            current_principal.principal = False
            current_principal.save(update_fields=["principal"])
    
    # Se estiver desmarcando como principal e era o único principal,
    # mantém como principal (não pode ficar sem endereço principal)
    if payload.get("principal") is False:
        principal_count = get_addresses_by_church(church.id).filter(principal=True).count()
        if principal_count == 1 and address.principal:
            payload["principal"] = True
    
    return update_church_address(address, **payload)


def delete_church_address_service(user: User, address_id: uuid.UUID) -> bool:
    """
    Deleta um endereço da igreja do usuário.
    Retorna True se deletou, False se não encontrou.
    """
    church = _get_church(user)
    if not church:
        return False
    
    address = get_address_by_id_and_church(address_id, church.id)
    if not address:
        return False
    
    # Verifica se é o único endereço
    address_count = get_addresses_by_church(church.id).count()
    if address_count == 1:
        # Não pode deletar o único endereço
        return False
    
    # Se o endereço deletado era principal, marca outro como principal
    was_principal = address.principal
    
    delete_church_address(address)
    
    if was_principal:
        new_principal = get_addresses_by_church(church.id).first()
        if new_principal:
            new_principal.principal = True
            new_principal.save(update_fields=["principal"])
    
    return True