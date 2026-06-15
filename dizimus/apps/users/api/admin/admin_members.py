"""
Admin — Members router.
Gestão global de membros: visão transversal que só o admin tem.
"""
import uuid
from typing import Optional

from ninja import Router, Query
from django.core.exceptions import ValidationError as DjangoValidationError

from dizimus.apps.users.permissions import AdminOnlyAuth
from dizimus.apps.users.schemas.member_schemas import MemberOut, MemberUpdateIn
from dizimus.apps.users.schemas.profile_member_schema import MemberProfileOut
from dizimus.apps.users.schemas.users_schemas import MessageOut
from dizimus.apps.users.selectors.member_selector import (
    get_all_members,
    get_member_by_id,
    search_members,
    get_members_by_birth_month,
)
from dizimus.apps.users import repositories
from dizimus.apps.users.utils.pagination import paginate_queryset, PageOut, PAGE_SIZE_DEFAULT

router = Router(tags=["Admin - Members"])


# ── Listagem ──────────────────────────────────────────────────────────────────

@router.get(
    "/",
    auth=AdminOnlyAuth(),
    response={200: PageOut[MemberOut]},
    summary="Lista todos os membros",
    description=(
        "Retorna membros de todas as igrejas com paginação. "
        "Use `search` para buscar por nome, cpf, telefone e endereço (cidade, bairro, cep e estado). "
        "Filtre por `birth_month` (1-12) para aniversariantes do mês."
    ),
)
def list_members(
    request,
    page: int = Query(1, ge=1),
    page_size: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=100),
    search: Optional[str] = Query(None, description="Busca por nome, cpf, telefone e endereço (cidade, bairro, cep e estado)"),
    birth_month: Optional[int] = Query(None, ge=1, le=12, description="Aniversariantes do mês (1-12)"),
):
    if search:
        qs = search_members(search)
    elif birth_month:
        qs = get_members_by_birth_month(birth_month)
    else:
        qs = get_all_members()

    qs = qs.select_related("user").order_by("first_name", "last_name")
    return 200, paginate_queryset(qs, page, page_size, MemberOut.from_orm)


# ── Detalhe e edição ──────────────────────────────────────────────────────────

@router.get(
    "/{member_id}",
    auth=AdminOnlyAuth(),
    response={200: MemberProfileOut, 404: MessageOut},
    summary="Perfil completo de um membro",
)
def get_member(request, member_id: uuid.UUID):
    member = get_member_by_id(member_id)
    if not member:
        return 404, {"detail": "Membro não encontrado."}
    return 200, MemberProfileOut.from_orm(member.user, member)


@router.patch(
    "/{member_id}",
    auth=AdminOnlyAuth(),
    response={200: MemberProfileOut, 404: MessageOut, 409: MessageOut, 422: MessageOut},
    summary="Edita dados de um membro",
)
def update_member(request, member_id: uuid.UUID, payload: MemberUpdateIn):
    member = get_member_by_id(member_id)
    if not member:
        return 404, {"detail": "Membro não encontrado."}

    data = payload.dict(exclude_unset=True)
    try:
        member = repositories.update_member_profile(member, **data)
        return 200, MemberProfileOut.from_orm(member.user, member)
    except DjangoValidationError as e:
        return 422, {"detail": str(e.message)}


# ── Remoção ───────────────────────────────────────────────────────────────────

@router.delete(
    "/{member_id}",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Remove um membro permanentemente",
    description="Remove o membro e o usuário vinculado. Ação irreversível.",
)
def delete_member(request, member_id: uuid.UUID):
    member = get_member_by_id(member_id)
    if not member:
        return 404, {"detail": "Membro não encontrado."}
    member.user.delete()
    return 200, {"detail": "Membro removido com sucesso."}