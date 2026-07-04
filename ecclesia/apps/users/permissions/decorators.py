"""
Decoradores e classes de permissão para Django Ninja.
"""
from functools import wraps
from typing import Union, List
from ninja_jwt.authentication import JWTAuth

from ecclesia.apps.users.permissions.checker_permissions import (
    MemberChurchPermissionChecker,
    MemberChurchAllPermissionsChecker,
)
from ecclesia.apps.users.permissions.request_helpers import get_church_id_from_request
from ecclesia.apps.users.exceptions.permissions import PermissionDenied


class HasPermission(JWTAuth):
    """
    Auth class para Django Ninja.
    Autentica via JWT + verifica se o membro tem QUALQUER UMA das permissões.

    Uso:
        @router.post("/members", auth=HasPermission("members.create"))
        def create_member(request): ...
    """

    def __init__(self, permission_code: Union[str, List[str]]):
        super().__init__()
        self.checker = MemberChurchPermissionChecker(permission_code)

    def authenticate(self, request, token: str):
        user = super().authenticate(request, token)
        if not user:
            return None

        if user.is_superuser:
            return user

        try:
            self.checker.check(request)
            return user
        except PermissionDenied:
            return None


class HasAllPermissions(JWTAuth):
    """
    Auth class para Django Ninja.
    Autentica via JWT + verifica se o membro tem TODAS as permissões.

    Uso:
        @router.delete("/members/{id}", auth=HasAllPermissions(["members.view", "members.delete"]))
        def delete_member(request): ...
    """

    def __init__(self, permission_codes: List[str]):
        super().__init__()
        self.checker = MemberChurchAllPermissionsChecker(permission_codes)

    def authenticate(self, request, token: str):
        user = super().authenticate(request, token)
        if not user:
            return None

        if user.is_superuser:
            return user

        try:
            self.checker.check(request)
            return user
        except PermissionDenied:
            return None


# ============================================================================
# Decorators alternativos (para uso com @decorator em vez de auth=)
# ============================================================================

def require_permission(permission_code: Union[str, List[str]]):
    """
    Decorator para verificar permissão em funções Django Ninja.

    Uso:
        @router.post("/members")
        @require_permission("members.create")
        def create_member(request): ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            checker = MemberChurchPermissionChecker(permission_code)
            try:
                checker.check(request)
            except PermissionDenied as e:
                from ecclesia.apps.users.schemas.users_schemas import MessageOut
                return 403, {"detail": str(e)}
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_all_permissions(permission_codes: List[str]):
    """
    Decorator para verificar TODAS as permissões.

    Uso:
        @router.delete("/members/{id}")
        @require_all_permissions(["members.view", "members.delete"])
        def delete_member(request): ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            checker = MemberChurchAllPermissionsChecker(permission_codes)
            try:
                checker.check(request)
            except PermissionDenied as e:
                return 403, {"detail": str(e)}
            return func(request, *args, **kwargs)
        return wrapper
    return decorator