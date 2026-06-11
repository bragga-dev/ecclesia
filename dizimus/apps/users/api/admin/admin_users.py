"""
Admin — Users router.

Gestão de contas de usuário: só o superusuário/admin executa.
Nota: admin não possui perfil de church nem member.
      Para ver/editar perfis, use /admin/churches/{id} e /admin/members/{id}.
"""
import uuid
from typing import Optional

from ninja import Router, Query

from dizimus.apps.users.permissions import AdminOnlyAuth
from dizimus.apps.users.models.user import User
from dizimus.apps.users.schemas.users_schemas import UserOut, MessageOut
from dizimus.apps.users.selectors.user import (
    get_user_by_id,
    get_all_users,
    get_users_by_role,
    get_active_users,
    get_inactive_users,
    search_users,
)
from dizimus.apps.users.utils.pagination import paginate_queryset, PageOut, PAGE_SIZE_DEFAULT

router = Router(tags=["Admin - Users"])


# ── Listagem ──────────────────────────────────────────────────────────────────

@router.get(
    "/",
    auth=AdminOnlyAuth(),
    response={200: PageOut[UserOut]},
    summary="Lista todos os usuários",
    description=(
        "Retorna todos os usuários com paginação. "
        "Filtre por `role` (member, church, admin) e `is_active` (true/false). "
        "Use `search` para buscar por e-mail."
    ),
)
def list_users(request, page: int = Query(1, ge=1),
    page_size: int = Query(PAGE_SIZE_DEFAULT, ge=1, le=100),
    role: Optional[str] = Query(None, description="Filtrar por role: member, church, admin"),
    is_active: Optional[bool] = Query(None, description="true = ativos · false = inativos"),
    search: Optional[str] = Query(None, description="Busca por e-mail"),):
    if search:
        qs = search_users(search)
    elif role:
        qs = get_users_by_role(role)
    elif is_active is True:
        qs = get_active_users()
    elif is_active is False:
        qs = get_inactive_users()
    else:
        qs = get_all_users()

    qs = qs.order_by("-date_joined")
    return 200, paginate_queryset(qs, page, page_size, lambda u: u)


@router.get(
    "/{user_id}",
    auth=AdminOnlyAuth(),
    response={200: UserOut, 404: MessageOut},
    summary="Detalhe de um usuário",
)
def get_user(request, user_id: uuid.UUID):
    user = get_user_by_id(user_id)
    if not user:
        return 404, {"detail": "Usuário não encontrado."}
    return 200, user


# ── Ativação / Desativação ────────────────────────────────────────────────────

@router.patch(
    "/{user_id}/activate",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Ativa uma conta de usuário",
)
def activate_user(request, user_id: uuid.UUID):
    user = get_user_by_id(user_id)
    if not user:
        return 404, {"detail": "Usuário não encontrado."}
    if user.is_active:
        return 200, {"detail": "Conta já está ativa."}
    user.is_active = True
    user.save(update_fields=["is_active"])
    return 200, {"detail": "Conta ativada."}


@router.patch(
    "/{user_id}/deactivate",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Desativa uma conta de usuário",
)
def deactivate_user(request, user_id: uuid.UUID):
    user = get_user_by_id(user_id)
    if not user:
        return 404, {"detail": "Usuário não encontrado."}
    if user.is_superuser:
        return 200, {"detail": "Não é possível desativar um superusuário."}
    user.is_active = False
    user.save(update_fields=["is_active"])
    return 200, {"detail": "Conta desativada."}


# ── Remoção ───────────────────────────────────────────────────────────────────

@router.delete(
    "/{user_id}",
    auth=AdminOnlyAuth(),
    response={200: MessageOut, 404: MessageOut},
    summary="Remove um usuário permanentemente",
    description="Remove o usuário e todos os dados vinculados. Ação irreversível.",
)
def delete_user(request, user_id: uuid.UUID):
    user = get_user_by_id(user_id)
    if not user:
        return 404, {"detail": "Usuário não encontrado."}
    if user.is_superuser:
        return 200, {"detail": "Não é possível remover um superusuário."}
    user.delete()
    return 200, {"detail": "Usuário removido com sucesso."}