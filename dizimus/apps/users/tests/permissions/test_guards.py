# test_guards.py
"""
Testes para as funções de guard (verificação de permissões).
"""
import pytest
from unittest.mock import Mock, patch
from dizimus.apps.users.exceptions import PermissionDenied
from dizimus.apps.users.models.user import User
from dizimus.apps.users.permissions.guards import(
    check_church_permission,
    check_permission,
    require_active,
    require_admin,
    require_church,
    require_member,
    require_role,
    require_verified,

)


class TestCheckPermission:
    """Testes para a função check_permission."""
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.is_superuser = True
        user.role = User.UserRole.ADMIN
        return user
    
    @pytest.fixture
    def church_user(self):
        user = Mock(spec=User)
        user.is_superuser = False
        user.role = User.UserRole.CHURCH
        return user
    
    @pytest.fixture
    def member_user(self):
        user = Mock(spec=User)
        user.is_superuser = False
        user.role = User.UserRole.MEMBER
        return user
    
    def test_check_permission_allows_admin_without_checks(self, admin_user):

        
        # Admin deve passar sem verificar as condições
        check_permission(admin_user, lambda u: False)
        # Não deve levantar exceção
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_permission_raises_when_check_fails(self, mock_is_admin, church_user):
        mock_is_admin.return_value = False
        
        with pytest.raises(PermissionDenied):
            check_permission(church_user, lambda u: False)
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_permission_passes_when_all_checks_pass(self, mock_is_admin, church_user):
        mock_is_admin.return_value = False
        
        # Não deve levantar exceção
        check_permission(church_user, lambda u: True)
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_permission_uses_custom_message(self, mock_is_admin, church_user):
        mock_is_admin.return_value = False
        
        custom_message = "Custom error message"
        with pytest.raises(PermissionDenied) as exc_info:
            check_permission(church_user, lambda u: False, message=custom_message)
        
        assert str(exc_info.value) == custom_message
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_permission_with_multiple_checks(self, mock_is_admin, church_user):
        mock_is_admin.return_value = False
        
        # Primeiro check passa, segundo falha
        with pytest.raises(PermissionDenied):
            check_permission(
                church_user,
                lambda u: True,
                lambda u: False,
                lambda u: True
            )


class TestCheckChurchPermission:
    """Testes para a função check_church_permission."""
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.is_superuser = True
        return user
    
    @pytest.fixture
    def regular_user(self):
        user = Mock(spec=User)
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def church(self):
        return Mock()
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_church_permission_allows_admin(self, mock_is_admin, admin_user, church):
        mock_is_admin.return_value = True
        
        # Admin deve passar sem verificar as condições
        check_church_permission(admin_user, church, lambda u, c: False)
        # Não deve levantar exceção
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_church_permission_raises_when_check_fails(self, mock_is_admin, regular_user, church):
        mock_is_admin.return_value = False
        
        with pytest.raises(PermissionDenied):
            check_church_permission(regular_user, church, lambda u, c: False)
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_church_permission_passes_when_all_checks_pass(self, mock_is_admin, regular_user, church):
        mock_is_admin.return_value = False
        
        check_church_permission(regular_user, church, lambda u, c: True)
        # Não deve levantar exceção
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_check_church_permission_uses_custom_message(self, mock_is_admin, regular_user, church):
        mock_is_admin.return_value = False
        custom_message = "Custom church error"
        with pytest.raises(PermissionDenied) as exc_info:
            check_church_permission(
                regular_user, 
                church, 
                lambda u, c: False, 
                message=custom_message
            )
        
        assert str(exc_info.value) == custom_message


class TestRequireFunctions:
    """Testes para as funções require_*."""
    @patch('dizimus.apps.users.permissions.roles.is_admin')
    def test_require_role_raises_for_wrong_role(self, mock_is_admin):
        mock_is_admin.return_value = False
        
        user = Mock(spec=User)
        # Criar um objeto role que se comporte como Enum
        class MockRole:
            value = "member"
        user.role = MockRole()  # Em vez de User.UserRole.MEMBER
        
        with pytest.raises(PermissionDenied) as exc_info:
            require_role("church")(user)
        
        assert "church" in str(exc_info.value).lower()
        
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_require_role_passes_for_correct_role(self, mock_is_admin):
        mock_is_admin.return_value = False
        
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        
        require_role("church")(user)  # Não deve levantar exceção
    
    @patch('dizimus.apps.users.permissions.guards.is_admin')
    def test_require_role_allows_admin_bypass(self, mock_is_admin):
        mock_is_admin.return_value = True
        
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        
        require_role("church")(user)  # Admin bypass, não deve levantar exceção