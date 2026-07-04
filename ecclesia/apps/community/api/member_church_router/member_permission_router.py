"""
Endpoints de gestão de permissões de membros em igrejas.

Auth é herdada do router pai (ChurchOnlyAuth).
Verificação granular de permissão feita dentro de cada endpoint
via MemberChurchPermissionChecker para compatibilidade com o Swagger.
"""
import uuid
from ninja import Router
from django_ratelimit.decorators import ratelimit
from django.core.exceptions import ValidationError, PermissionDenied

from ecclesia.apps.users.schemas.users_schemas import MessageOut
from ecclesia.apps.users.schemas.member_permission_schema import (
    SystemPermissionOut,
    MemberPermissionOut,
    GrantPermissionIn,
    UpdatePermissionIn,
)
from ecclesia.apps.users.selectors.member_permission_selector import (
    get_all_system_permissions,
    get_member_permissions,
    get_member_church,
)
from ecclesia.apps.users.services.member_permission_service import (
    grant_permission,
    update_permission,
    revoke_permission,
)
from ecclesia.apps.users.permissions.checker_permissions import (
    MemberChurchPermissionChecker,
)

router = Router(tags=["Member Permissions"])

_view_checker = MemberChurchPermissionChecker("permissions.view")
_manage_checker = MemberChurchPermissionChecker("permissions.manage")


# ============================================================
# CATÁLOGO — permissões disponíveis no sistema
# ============================================================
@router.get(
    "/permissions/available",
    response={200: list[SystemPermissionOut]},
    summary="Listar permissões disponíveis no sistema",
    description="Retorna o catálogo completo de permissões que podem ser atribuídas.",
)
@ratelimit(key="user", rate="30/m", block=True)
def list_available_permissions(request):
    permissions = get_all_system_permissions()
    return 200, [
        SystemPermissionOut(
            id=p.id,
            code=p.code,
            name=p.name,
            module=p.module,
            description=p.description,
            is_active=p.is_active,
        )
        for p in permissions
    ]


# ============================================================
# LISTAR permissões de um membro em uma igreja
# ============================================================
@router.get(
    "/{church_id}/members/{member_id}/permissions",
    response={200: list[MemberPermissionOut], 403: MessageOut, 404: MessageOut},
    summary="Listar permissões de um membro",
)
@ratelimit(key="user", rate="60/m", block=True)
def list_member_permissions(
    request,
    church_id: uuid.UUID,
    member_id: uuid.UUID,
):
    try:
        _view_checker.check(request)
    except PermissionDenied as e:
        return 403, {"detail": str(e)}

    member_church = get_member_church(member_id=member_id, church_id=church_id)
    if not member_church:
        return 404, {"detail": "Membro não encontrado ou sem vínculo ativo nesta igreja."}

    permissions = get_member_permissions(member_church)
    return 200, [MemberPermissionOut.from_orm(p) for p in permissions]


# ============================================================
# ATRIBUIR permissão a um membro
# ============================================================
@router.post(
    "/{church_id}/members/{member_id}/permissions",
    response={201: MemberPermissionOut, 400: MessageOut, 403: MessageOut, 404: MessageOut, 409: MessageOut},
    summary="Atribuir permissão a um membro",
)
@ratelimit(key="user", rate="30/m", block=True)
def grant_member_permission(
    request,
    church_id: uuid.UUID,
    member_id: uuid.UUID,
    payload: GrantPermissionIn,
):
    try:
        _manage_checker.check(request)
    except PermissionDenied as e:
        return 403, {"detail": str(e)}

    try:
        permission = grant_permission(
            member_id=member_id,
            church_id=church_id,
            permission_code=payload.permission_code,
            granted_by=request.user,
            expires_at=payload.expires_at,
        )
    except ValidationError as e:
        msg = str(e)
        if "não encontrado" in msg:
            return 404, {"detail": msg}
        if "já possui" in msg:
            return 409, {"detail": msg}
        return 400, {"detail": msg}

    return 201, MemberPermissionOut.from_orm(permission)


# ============================================================
# ATUALIZAR permissão (ativar/desativar, alterar expiração)
# ============================================================
@router.patch(
    "/{church_id}/members/{member_id}/permissions/{permission_id}",
    response={200: MemberPermissionOut, 400: MessageOut, 403: MessageOut, 404: MessageOut},
    summary="Atualizar permissão de um membro",
    description="Permite ativar/desativar ou alterar a data de expiração.",
)
@ratelimit(key="user", rate="30/m", block=True)
def update_member_permission(
    request,
    church_id: uuid.UUID,
    member_id: uuid.UUID,
    permission_id: uuid.UUID,
    payload: UpdatePermissionIn,
):
    try:
        _manage_checker.check(request)
    except PermissionDenied as e:
        return 403, {"detail": str(e)}

    try:
        permission = update_permission(
            permission_id=permission_id,
            member_id=member_id,
            church_id=church_id,
            is_active=payload.is_active,
            expires_at=payload.expires_at,
        )
    except ValidationError as e:
        msg = str(e)
        if "não encontrado" in msg:
            return 404, {"detail": msg}
        return 400, {"detail": msg}

    return 200, MemberPermissionOut.from_orm(permission)


# ============================================================
# REVOGAR permissão (delete permanente)
# ============================================================
@router.delete(
    "/{church_id}/members/{member_id}/permissions/{permission_id}",
    response={204: None, 400: MessageOut, 403: MessageOut, 404: MessageOut},
    summary="Revogar permissão de um membro",
)
@ratelimit(key="user", rate="30/m", block=True)
def revoke_member_permission(
    request,
    church_id: uuid.UUID,
    member_id: uuid.UUID,
    permission_id: uuid.UUID,
):
    try:
        _manage_checker.check(request)
    except PermissionDenied as e:
        return 403, {"detail": str(e)}

    try:
        revoke_permission(
            permission_id=permission_id,
            member_id=member_id,
            church_id=church_id,
        )
    except ValidationError as e:
        msg = str(e)
        if "não encontrado" in msg:
            return 404, {"detail": msg}
        return 400, {"detail": msg}

    return 204, None