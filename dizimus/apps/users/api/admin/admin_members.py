"""
Admin — Members router.

Listagem global de membros: visão transversal que só o admin tem.
"""
import uuid
from typing import List, Optional

from ninja import Router, Query

from dizimus.apps.users.permissions import AdminOnlyAuth
from dizimus.apps.users.schemas.member_schemas import MemberOut
from dizimus.apps.users.schemas.users_schemas import MessageOut
from dizimus.apps.users.selectors.member_selector import (
    get_all_members,
    get_member_by_id,
    search_members,
    get_members_by_contribution,
)

router = Router(tags=["Admin - Members"])


@router.get(
    "/",
    auth=AdminOnlyAuth(),
    response={200: List[MemberOut]},
    summary="Lista todos os membros",
    description="Retorna membros de todas as igrejas. Suporta filtro por tipo de contribuição e busca por nome/CPF.",
)
def list_members(
    request,
    search: Optional[str] = Query(None, description="Busca por nome ou CPF"),
    contribution: Optional[str] = Query(None, description="Filtrar por tipo: none, dizimista, ofertante, both"),
):
    if search:
        qs = search_members(search)
    elif contribution:
        qs = get_members_by_contribution(contribution)
    else:
        qs = get_all_members()

    qs = qs.select_related("user")
    return 200, [MemberOut.from_orm(m) for m in qs]


@router.get(
    "/{member_id}",
    auth=AdminOnlyAuth(),
    response={200: MemberOut, 404: MessageOut},
    summary="Detalhe de um membro",
)
def get_member(request, member_id: uuid.UUID):
    member = get_member_by_id(member_id)
    if not member:
        return 404, {"detail": "Membro não encontrado."}
    return 200, MemberOut.from_orm(member)