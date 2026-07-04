"""
Permissions - Módulo de controle de acesso.
"""
from .roles import (
    # Role checks
    is_church,
    is_member,
    is_admin,
    is_superuser,
    # Status checks
    is_active,
    is_trusty,
    is_verified,
    is_staff,
    # Church membership checks
    has_role_in_church,
    is_church_admin,
    is_pastor,
    is_treasurer,
    is_secretary,
    is_member_of_church,
    # Ownership checks
    is_owner,
    is_church_owner,
    is_member_owner,
    # Combinators
    has_any_role,
    has_all_roles,
    can_manage_church,
    can_view_finances,
)

from .guards import (
    check_permission,
    check_church_permission,
    require_active,
    require_verified,
    require_role,
    require_church,
    require_member,
    require_admin,
)

from .auth_classes import (
    ChurchOnlyAuth,
    MemberOnlyAuth,
    AdminOnlyAuth,
    ActiveUserAuth,
    VerifiedUserAuth,
)

from ecclesia.apps.users.permissions.checker_permissions import (
    MemberChurchPermissionChecker,
    MemberChurchAllPermissionsChecker,
)
from ecclesia.apps.users.permissions.decorators import (
    require_permission,
    require_all_permissions,
    HasPermission,
    HasAllPermissions,
)

__all__ = [
    # Roles
    "is_church",
    "is_member", 
    "is_admin",
    "is_superuser",
    "is_active",
    "is_trusty",
    "is_verified",
    "is_staff",
    # Church membership
    "has_role_in_church",
    "is_church_admin",
    "is_pastor",
    "is_treasurer",
    "is_secretary",
    "is_member_of_church",
    # Ownership
    "is_owner",
    "is_church_owner",
    "is_member_owner",
    # Combinators
    "has_any_role",
    "has_all_roles",
    "can_manage_church",
    "can_view_finances",
    # Guards
    "check_permission",
    "check_church_permission",
    "require_active",
    "require_verified",
    "require_role",
    "require_church",
    "require_member",
    "require_admin",
    # Auth classes
    "ChurchOnlyAuth",
    "MemberOnlyAuth",
    "AdminOnlyAuth",
    "ActiveUserAuth",
    "VerifiedUserAuth",
    # Checkers
    'MemberChurchPermissionChecker',
    'MemberChurchAllPermissionsChecker',
    'require_permission',
    'require_all_permissions',
    'HasPermission',
    'HasAllPermissions',
]