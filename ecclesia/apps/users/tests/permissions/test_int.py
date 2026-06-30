# test_init.py
"""
Testes para verificar que o __init__ exporta corretamente todos os símbolos.
"""
import pytest
from ecclesia.apps.users.permissions import (
    # Roles
    is_church, is_member, is_admin, is_superuser,
    is_active, is_trusty, is_verified, is_staff,
    has_role_in_church, is_church_admin, is_pastor,
    is_treasurer, is_secretary, is_member_of_church,
    is_owner, is_church_owner, is_member_owner,
    has_any_role, has_all_roles, can_manage_church, can_view_finances,
    # Guards
    check_permission, check_church_permission,
    require_active, require_verified, require_role,
    require_church, require_member, require_admin,
    # Auth classes
    ChurchOnlyAuth, MemberOnlyAuth, AdminOnlyAuth,
    ActiveUserAuth, VerifiedUserAuth,
)


class TestInitExports:
    """Testes para verificar que todos os símbolos são exportados corretamente."""
    
    def test_all_roles_are_exported(self):
        """Verifica que todas as funções de role estão exportadas."""
        # Role checks
        assert is_church is not None
        assert is_member is not None
        assert is_admin is not None
        assert is_superuser is not None
        
        # Status checks
        assert is_active is not None
        assert is_trusty is not None
        assert is_verified is not None
        assert is_staff is not None
        
        # Church membership checks
        assert has_role_in_church is not None
        assert is_church_admin is not None
        assert is_pastor is not None
        assert is_treasurer is not None
        assert is_secretary is not None
        assert is_member_of_church is not None
        
        # Ownership checks
        assert is_owner is not None
        assert is_church_owner is not None
        assert is_member_owner is not None
        
        # Combinators
        assert has_any_role is not None
        assert has_all_roles is not None
        assert can_manage_church is not None
        assert can_view_finances is not None
    
    def test_all_guards_are_exported(self):
        """Verifica que todas as funções de guard estão exportadas."""
        assert check_permission is not None
        assert check_church_permission is not None
        assert require_active is not None
        assert require_verified is not None
        assert require_role is not None
        assert require_church is not None
        assert require_member is not None
        assert require_admin is not None
    
    def test_all_auth_classes_are_exported(self):
        """Verifica que todas as classes de autenticação estão exportadas."""
        assert ChurchOnlyAuth is not None
        assert MemberOnlyAuth is not None
        assert AdminOnlyAuth is not None
        assert ActiveUserAuth is not None
        assert VerifiedUserAuth is not None