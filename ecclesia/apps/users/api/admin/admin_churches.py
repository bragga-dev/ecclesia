"""
Admin — Churches router.
Operações transversais de igrejas: só o superusuário/admin executa.
"""
import uuid
from typing import Optional

from ninja import Router, Query
from django.core.exceptions import ValidationError as DjangoValidationError

from ecclesia.apps.users.permissions import AdminOnlyAuth
from ecclesia.apps.users.models import Church
from ecclesia.apps.users.schemas.church_schemas import ChurchOut, ChurchUpdateIn
from ecclesia.apps.users.schemas.profile_church_schema import ChurchProfileOut
from ecclesia.apps.users.schemas.users_schemas import MessageOut
from ecclesia.apps.users.selectors.church_selector import (
    get_all_churches,
    get_verified_churches,
    get_unverified_churches,
    get_church_by_id,
    search_churches,
)
from ecclesia.apps.users import repositories
from ecclesia.apps.users.utils.pagination import paginate_queryset, PageOut, PAGE_SIZE_DEFAULT
from ecclesia.apps.community.schemas.member_church_schema import ChurchMemberListOut
from ecclesia.apps.community.services.member_church_service import list_member_church_service
from ecclesia.apps.community.models.member_church_model import MemberChurch

router = Router(tags=["Admin - Churches"])


# ── Listagem ──────────────────────────────────────────────────────────────────

@router.get(
    "/",
    auth=AdminOnlyAuth(),
    response={200: PageOut[ChurchOut]},
    summary="Lista todas as igrejas",
    description=(
        "Retorna todas as igrejas cadastradas com paginação. "
        "Filtre por `verified=true/false` ou busque por nome, CNPJ e cidade com `search`."
    ),
)
def list_churches(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=100),
    verified: Optional[bool] = Query(None, description="true = verificadas · false = pendentes"),
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

    qs = qs.select_related("user").order_by("-user__date_joined")
    return 200, paginate_queryset(qs, page, page_size, ChurchOut.from_orm)


@router.get(
    "/{church_id}",
    auth=AdminOnlyAuth(),
    response={200: ChurchProfileOut, 404: MessageOut},
    summary="Perfil completo de uma igreja",
)
def get_church(request, church_id: uuid.UUID):
    church = get_church_by_id(church_id)
    if not church:
        return 404, {"detail": "Igreja não encontrada."}
    return 200, ChurchProfileOut.from_orm(church.user, church)


# ── Edição ────────────────────────────────────────────────────────────────────

@router.patch(
    "/{church_id}",
    auth=AdminOnlyAuth(),
    response={200: ChurchProfileOut, 404: MessageOut, 409: MessageOut, 422: MessageOut},
    summary="Edita dados de uma igreja",
)
def update_church(request, church_id: uuid.UUID, payload: ChurchUpdateIn):
    church = get_church_by_id(church_id)
    if not church:
        return 404, {"detail": "Igreja não encontrada."}

    data = payload.dict(exclude_unset=True)
    try:
        church = repositories.update_church_profile(church, **data)
        return 200, ChurchProfileOut.from_orm(church.user, church)
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


# ── Verificação ───────────────────────────────────────────────────────────────

@router.patch(
    "/{church_id}/verify",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Verifica (aprova) uma igreja",
)
def verify_church(request, church_id: uuid.UUID):
    church = get_church_by_id(church_id)
    if not church:
        return 404, {"detail": "Igreja não encontrada."}
    if church.is_verified:
        return 200, {"detail": "Igreja já está verificada."}
    repositories.set_church_as_verified(church)
    return 200, {"detail": "Igreja verificada com sucesso."}


@router.patch(
    "/{church_id}/unverify",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Revoga verificação de uma igreja",
)
def unverify_church(request, church_id: uuid.UUID):
    church = get_church_by_id(church_id)
    if not church:
        return 404, {"detail": "Igreja não encontrada."}
    repositories.set_church_as_unverified(church)
    return 200, {"detail": "Verificação revogada."}


# ── Membros da igreja ─────────────────────────────────────────────────────────

@router.get(
    "/{church_id}/members",
    auth=AdminOnlyAuth(),
    response={200: PageOut[ChurchMemberListOut], 404: MessageOut},
    summary="Lista membros de uma igreja específica",
    description="Visão transversal: o admin vê os membros de qualquer igreja.",
)
def list_church_members(
    request,
    church_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filtrar por status: active, inactive, pending"),
):
    church = get_church_by_id(church_id)
    if not church:
        return 404, {"detail": "Igreja não encontrada."}

    memberships = list_member_church_service(
        church_id=church_id,
        status=status,
    )
    return 200, paginate_queryset(memberships, page, page_size, ChurchMemberListOut.from_membership)


# ── Remoção ───────────────────────────────────────────────────────────────────

@router.delete(
    "/{church_id}",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Remove uma igreja permanentemente",
    description="Remove a igreja e o usuário vinculado. Ação irreversível.",
)
def delete_church(request, church_id: uuid.UUID):
    church = get_church_by_id(church_id)
    if not church:
        return 404, {"detail": "Igreja não encontrada."}
    church.user.delete()
    return 200, {"detail": "Igreja removida com sucesso."}