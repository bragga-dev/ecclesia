"""
Admin — Churches router.

Operações transversais de igrejas: só o superusuário/admin executa.
"""
import uuid
from typing import List, Optional

from ninja import Router, Query
from django.shortcuts import get_object_or_404

from dizimus.apps.users.permissions import AdminOnlyAuth
from dizimus.apps.users.models import Church, User
from dizimus.apps.users.schemas.church_schemas import ChurchOut
from dizimus.apps.users.schemas.users_schemas import MessageOut
from dizimus.apps.users.selectors.church_selector import (
    get_all_churches,
    get_verified_churches,
    get_unverified_churches,
    search_churches,
)

router = Router(tags=["Admin - Churches"])


# ── Listagem ──────────────────────────────────────────────────────────────────

@router.get(
    "/",
    auth=AdminOnlyAuth(),
    response={200: List[ChurchOut]},
    summary="Lista todas as igrejas",
    description="Retorna todas as igrejas cadastradas no sistema. Suporta filtro por status e busca por nome/CNPJ/cidade.",
)
def list_churches(
    request,
    verified: Optional[bool] = Query(None, description="true = verificadas, false = não verificadas"),
    search: Optional[str] = Query(None, description="Busca por nome, CNPJ ou cidade"),
):
    if search:
        qs = search_churches(search)
    elif verified is True:
        qs = get_verified_churches()
    elif verified is False:
        qs = get_unverified_churches()
    else:
        qs = get_all_churches()

    qs = qs.select_related("user")
    return 200, [ChurchOut.from_orm(church) for church in qs]


@router.get(
    "/{church_id}",
    auth=AdminOnlyAuth(),
    response={200: ChurchOut, 404: MessageOut},
    summary="Detalhe de uma igreja",
    description="Retorna os dados completos de qualquer igreja pelo ID.",
)
def get_church(request, church_id: uuid.UUID):
    church = (
        Church.objects
        .select_related("user")
        .filter(pk=church_id)
        .first()
    )
    if not church:
        return 404, {"detail": "Igreja não encontrada."}
    return 200, ChurchOut.from_orm(church)


# ── Verificação ───────────────────────────────────────────────────────────────

@router.patch(
    "/{church_id}/verify",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Verifica (aprova) uma igreja",
    description="Marca a igreja como verificada/aprovada pelo administrador.",
)
def verify_church(request, church_id: uuid.UUID):
    church = Church.objects.filter(pk=church_id).first()
    if not church:
        return 404, {"detail": "Igreja não encontrada."}

    if church.is_verified:
        return 200, {"detail": "Igreja já está verificada."}

    church.is_verified = True
    church.save(update_fields=["is_verified"])
    return 200, {"detail": "Igreja verificada com sucesso."}


@router.patch(
    "/{church_id}/unverify",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Remove verificação de uma igreja",
    description="Revoga a verificação de uma igreja.",
)
def unverify_church(request, church_id: uuid.UUID):
    church = Church.objects.filter(pk=church_id).first()
    if not church:
        return 404, {"detail": "Igreja não encontrada."}

    church.is_verified = False
    church.save(update_fields=["is_verified"])
    return 200, {"detail": "Verificação revogada."}


# ── Remoção ───────────────────────────────────────────────────────────────────

@router.delete(
    "/{church_id}",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Remove uma igreja",
    description="Remove permanentemente uma igreja e seu usuário vinculado.",
)
def delete_church(request, church_id: uuid.UUID):
    church = Church.objects.select_related("user").filter(pk=church_id).first()
    if not church:
        return 404, {"detail": "Igreja não encontrada."}

    user = church.user
    user.delete()  # CASCADE remove o Church junto
    return 200, {"detail": "Igreja removida com sucesso."}