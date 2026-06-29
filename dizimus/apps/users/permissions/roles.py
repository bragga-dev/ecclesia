"""
Roles - Funções que verificam o tipo e estado do usuário.
"""
from dizimus.apps.users.models import User
from dizimus.apps.community.models.member_church_model import MemberChurch


# ═══════════════════════════════════════════════════════════════════════════════
# Verificações de Role (tipo de usuário)
# ═══════════════════════════════════════════════════════════════════════════════

def is_church(user: User) -> bool:
    """Verifica se o usuário é uma Igreja."""
    return user.role == User.UserRole.CHURCH


def is_member(user: User) -> bool:
    """Verifica se o usuário é um Membro."""
    return user.role == User.UserRole.MEMBER


def is_admin(user: User) -> bool:
    """
    Verifica se o usuário é ADMIN (superuser ou role admin).
    ADMINS têm poderes especiais e bypass em várias verificações.
    """
    return user.is_superuser or user.role == User.UserRole.ADMIN


def is_superuser(user: User) -> bool:
    """Verifica se o usuário é superuser (root do sistema)."""
    return user.is_superuser


# ═══════════════════════════════════════════════════════════════════════════════
# Verificações de Estado
# ═══════════════════════════════════════════════════════════════════════════════

def is_active(user: User) -> bool:
    """Verifica se o usuário está ativo (conta aprovada/ativada)."""
    return user.is_active


def is_trusty(user: User) -> bool:
    """Verifica se o usuário é confiável (email verificado)."""
    return user.is_trusty


def is_verified(user: User) -> bool:
    """
    Verifica se o usuário é confiável E ativo.
    Combinação usada para acesso completo ao sistema.
    """
    return user.is_trusty and user.is_active


def is_staff(user: User) -> bool:
    """Verifica se o usuário é staff (acesso ao admin Django)."""
    return user.is_staff


# ═══════════════════════════════════════════════════════════════════════════════
# Verificações de Permissão no Vínculo (MemberChurch)
# ═══════════════════════════════════════════════════════════════════════════════

def has_role_in_church(user: User, church, required_role: str) -> bool:
    """
    Verifica se o usuário tem uma função específica dentro de uma igreja.
    
    Args:
        user: Usuário autenticado
        church: Instância da igreja
        required_role: Role necessária (ex: "pastor/padre", "admin")
    
    Returns:
        bool: True se o usuário tem a função na igreja
    """
    if is_admin(user):
        return True
    
    if not is_member(user):
        return False
    
    try:
        membership = user.member.church_memberships.get(
            church=church,
            status=MemberChurch.Status.ACTIVE
        )
        return membership.role == required_role
    except Exception:
        return False


def is_church_admin(user: User, church) -> bool:
    """Verifica se o usuário é administrador da igreja."""
    return has_role_in_church(user, church, MemberChurch.Role.CHURCH_ADMIN)


def is_pastor(user: User, church) -> bool:
    """Verifica se o usuário é pastor/padre da igreja."""
    return has_role_in_church(user, church, MemberChurch.Role.PASTOR)


def is_treasurer(user: User, church) -> bool:
    """Verifica se o usuário é tesoureiro da igreja."""
    return has_role_in_church(user, church, MemberChurch.Role.TREASURER)


def is_secretary(user: User, church) -> bool:
    """Verifica se o usuário é secretário da igreja."""
    return has_role_in_church(user, church, MemberChurch.Role.SECRETARY)


def is_member_of_church(user: User, church) -> bool:
    """Verifica se o usuário é membro ativo da igreja (qualquer função)."""
    if is_admin(user):
        return True
    
    if not is_member(user):
        return False
    
    return user.member.church_memberships.filter(
        church=church,
        status=MemberChurch.Status.ACTIVE
    ).exists()


# ═══════════════════════════════════════════════════════════════════════════════
# Verificações de Ownership (dono do recurso)
# ═══════════════════════════════════════════════════════════════════════════════

def is_owner(user: User, resource_user_id) -> bool:
    """Verifica se o usuário é o dono do recurso (pelo user_id)."""
    return str(user.id) == str(resource_user_id)


def is_church_owner(user: User, church) -> bool:
    """Verifica se o usuário é o dono (user) da igreja."""
    return user == church.user


def is_member_owner(user: User, member) -> bool:
    """Verifica se o usuário é o dono (user) do membro."""
    return user == member.user


# ═══════════════════════════════════════════════════════════════════════════════
# Combinadores
# ═══════════════════════════════════════════════════════════════════════════════

def has_any_role(user: User, roles: list) -> bool:
    """Verifica se o usuário tem alguma das roles especificadas."""
    return user.role in roles


def has_all_roles(user: User, roles: list) -> bool:
    """Verifica se o usuário tem todas as roles especificadas."""
    return all(user.role == role for role in roles)


def can_manage_church(user: User, church) -> bool:
    """
    Verifica se o usuário pode gerenciar a igreja.
    
    Quem pode:
    - Admin do sistema
    - Dono da igreja (user que criou)
    - Administrador da igreja (CHURCH_ADMIN)
    """
    return (
        is_admin(user) or
        is_church_owner(user, church) or
        is_church_admin(user, church) or
        is_pastor(user, church) or
        is_treasurer(user, church) or
        is_secretary(user, church)
    )


def can_view_finances(user: User, church) -> bool:
    """
    Verifica se o usuário pode ver finanças da igreja.
    
    Quem pode:
    - Admin do sistema
    - Dono da igreja
    - Pastor
    - Tesoureiro
    - Administrador da igreja
    """
    return (
        is_admin(user) or
        is_church_owner(user, church) or
        is_pastor(user, church) or
        is_treasurer(user, church) or
        is_church_admin(user, church)
    )