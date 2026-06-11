"""
Admin — Users router.

Operações de gestão de contas de usuário: só o superusuário/admin executa.
"""
import uuid
from typing import List, Optional

from ninja import Router, Query

from dizimus.apps.users.permissions import AdminOnlyAuth
from dizimus.apps.users.models import User
from dizimus.apps.users.schemas.users_schemas import UserOut, MessageOut
from dizimus.apps.users.selectors.user import get_user_by_id

router = Router(tags=["Admin - Users"])


# ── Listagem ──────────────────────────────────────────────────────────────────

@router.get(
    "/",
    auth=AdminOnlyAuth(),
    response={200: List[UserOut]},
    summary="Lista todos os usuários",
    description="Retorna todos os usuários cadastrados. Suporta filtro por role e estado.",
)
def list_users(
    request,
    role: Optional[str] = Query(None, description="Filtrar por role: member, church, admin"),
    is_active: Optional[bool] = Query(None, description="Filtrar por conta ativa/inativa"),
):
    qs = User.objects.all().order_by("-date_joined")

    if role:
        qs = qs.filter(role=role)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)

    return 200, list(qs)


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
    summary="Remove um usuário",
    description="Remove permanentemente o usuário e todos os dados vinculados (perfil, endereços).",
)
def delete_user(request, user_id: uuid.UUID):
    user = get_user_by_id(user_id)
    if not user:
        return 404, {"detail": "Usuário não encontrado."}

    if user.is_superuser:
        return 200, {"detail": "Não é possível remover um superusuário."}

    user.delete()
    return 200, {"detail": "Usuário removido com sucesso."}