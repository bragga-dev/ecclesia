"""
Guards - Funções que bloqueiam ou permitem acesso.
"""
from dizimus.apps.users.exceptions import PermissionDenied
from dizimus.apps.users.permissions import roles as _roles
from .roles import is_admin, is_active, is_verified


def check_permission(user, *checks, message: str = None) -> None:
    """
    Verifica se o usuário atende a TODAS as condições.
    
    Args:
        user: Usuário autenticado
        *checks: Funções de verificação (is_church, is_member, etc.)
        message: Mensagem personalizada de erro
    
    Raises:
        PermissionDenied: Se alguma verificação falhar
    
    Exemplos:
        check_permission(user, is_church)
        check_permission(user, is_member, is_verified)
    """
    # Admin bypass - superusuário tem acesso total
    if is_admin(user):
        return
    
    for check in checks:
        if not check(user):
            raise PermissionDenied(message)


def check_church_permission(user, church, *checks, message: str = None) -> None:
    """
    Verifica permissões que envolvem uma igreja específica.
    
    Args:
        user: Usuário autenticado
        church: Instância da igreja
        *checks: Funções que recebem (user, church)
        message: Mensagem personalizada de erro
    """
    if is_admin(user):
        return
    
    for check in checks:
        if not check(user, church):
            raise PermissionDenied(message)


def require_active(user) -> None:
    """Requer que o usuário esteja ativo."""
    if is_admin(user):
        return
    if not is_active(user):
        raise PermissionDenied("Sua conta não está ativa. Verifique seu e-mail.")


def require_verified(user) -> None:
    """Requer que o usuário seja verificado (trusty + active)."""
    if not is_verified(user):
        raise PermissionDenied(
            "Verifique seu e-mail antes de continuar. "
            "Verifique sua caixa de spam ou solicite um novo link."
        )

def require_role(role):
    role_value = role.value if hasattr(role, 'value') else role

    def decorator(user):
        if not _roles.is_admin(user):
            user_role_value = user.role.value if hasattr(user.role, 'value') else user.role
            if user_role_value != role_value:
                raise PermissionDenied(f"Acesso restrito a {role_value}s.")
        return True
    return decorator


# Criando verificadores específicos
require_church = require_role("church")
require_member = require_role("member")
require_admin = require_role("admin")