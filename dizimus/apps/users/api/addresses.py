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

@router.get(
    "/me/addresses",
    response=List[AddressOut],
    summary="Listar endereços",
)
def list_addresses(request):
    """Retorna todos os endereços do usuário. O endereço principal aparece primeiro."""
    return services.list_my_addresses(request.auth)


@router.post(
    "/me/addresses",
    response={201: AddressOut, 422: MessageOut},
    summary="Adicionar endereço",
    description=(
        "Cria um novo endereço para o usuário. "
        "Se `principal=true`, os demais endereços são automaticamente desmarcados como principal."
    ),
)
def create_address(request, payload: AddressIn):
    try:
        address = services.create_my_address(request.auth, payload)
        return 201, address
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.patch(
    "/me/addresses/{address_id}",
    response={200: AddressOut, 404: MessageOut, 422: MessageOut},
    summary="Atualizar endereço",
)
def update_address(request, address_id: uuid.UUID, payload: AddressUpdateIn):
    try:
        address = services.update_my_address(request.auth, address_id, payload)
        if not address:
            return 404, {"detail": "Endereço não encontrado."}
        return 200, address
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


@router.delete(
    "/me/addresses/{address_id}",
    response={200: MessageOut, 404: MessageOut},
    summary="Remover endereço",
)
def delete_address(request, address_id: uuid.UUID):
    deleted = services.delete_my_address(request.auth, address_id)
    if not deleted:
        return 404, {"detail": "Endereço não encontrado."}
    return 200, {"detail": "Endereço removido com sucesso."}