"""
Users router — endpoints de endereços.
"""
import uuid
from typing import List

from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import Router

from dizimus.apps.users import services
from dizimus.apps.users.schemas.addresses_schemas import (
    AddressIn,
    AddressOut,
    AddressUpdateIn,
)
from dizimus.apps.users.schemas.users_schemas import MessageOut

router = Router()

# ═══════════════════════════════════════════════════════════════════════════════
# ENDEREÇOS
# Funciona para Church e Member — o service detecta o role automaticamente.
# ═══════════════════════════════════════════════════════════════════════════════

from dizimus.apps.users.models import User

@router.get("/me/addresses", response=List[AddressOut], summary="Listar endereços")
def list_addresses(request):
    user: User = request.auth
    if user.role == User.UserRole.CHURCH:
        return services.list_church_addresses(user)
    return services.list_member_addresses(user)


@router.post("/me/addresses", response={201: AddressOut, 422: MessageOut}, summary="Adicionar endereço")
def create_address(request, payload: AddressIn):
    user: User = request.auth
    try:
        if user.role == User.UserRole.CHURCH:
            address = services.create_church_address_service(user, payload)
        else:
            address = services.create_member_address_service(user, payload)
        return 201, address
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.patch("/me/addresses/{address_id}", response={200: AddressOut, 404: MessageOut, 422: MessageOut})
def update_address(request, address_id: uuid.UUID, payload: AddressUpdateIn):
    user: User = request.auth
    try:
        if user.role == User.UserRole.CHURCH:
            address = services.update_church_address_service(user, address_id, payload)
        else:
            address = services.update_member_address_service(user, address_id, payload)
        if not address:
            return 404, {"detail": "Endereço não encontrado."}
        return 200, address
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.delete("/me/addresses/{address_id}", response={200: MessageOut, 400: MessageOut, 404: MessageOut}, summary="Deleta endereço pelo id")
def delete_address(request, address_id: uuid.UUID):
    user: User = request.auth

    # Verifica se o endereço existe antes de tentar deletar
    from dizimus.apps.users.selectors.church_selector import get_address_by_id_and_church
    from dizimus.apps.users.selectors.member_selector import get_address_by_id_and_member
    from dizimus.apps.users.selectors.church_selector import get_church_by_user_id
    from dizimus.apps.users.selectors.member_selector import get_member_by_user_id

    if user.role == User.UserRole.CHURCH:
        church = get_church_by_user_id(user.id)
        if not church or not get_address_by_id_and_church(address_id, church.id):
            return 404, {"detail": "Endereço não encontrado."}
        deleted = services.delete_church_address_service(user, address_id)
    else:
        member = get_member_by_user_id(user.id)
        if not member or not get_address_by_id_and_member(address_id, member.id):
            return 404, {"detail": "Endereço não encontrado."}
        deleted = services.delete_member_address_service(user, address_id)

    if not deleted:
        return 400, {"detail": "Não é possível remover o único endereço cadastrado."}
    return 200, {"detail": "Endereço removido com sucesso."}


@router.get("/me/addresses/{address_id}", response={200: AddressOut, 404: MessageOut}, summary="Exibe um único endereço")
def get_addresses(request, address_id: uuid.UUID):
    user: User = request.auth
    if user.role == User.UserRole.CHURCH:
        address = services.get_church_address_detail(user, address_id)
    else:
        address = services.get_member_address_detail(user, address_id)
    if not address:
        return 404, {"detail": "Endereço não encontrado."}
    return 200, address