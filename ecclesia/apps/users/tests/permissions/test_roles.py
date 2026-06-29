# test_roles.py
"""
Testes para as funções de verificação de roles e permissões.
"""
import pytest
from unittest.mock import Mock, patch
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.models.church import Church
from ecclesia.apps.community.models.member_church_model import MemberChurch
from ecclesia.apps.users.permissions.roles import (
    
is_church,
is_member,
is_admin,
is_active,
is_superuser,
is_verified,
is_trusty,
is_staff,
has_role_in_church,
is_church_admin,
is_pastor,
is_member_of_church,
is_member_owner,
is_church_owner,
is_secretary,
has_any_role,
is_treasurer,
has_all_roles,
can_view_finances,
can_manage_church,
is_owner,

)

class TestUserRoleChecks:
    """Testes para verificações de role do usuário."""
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.ADMIN
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def superuser(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        user.is_superuser = True
        return user
    
    @pytest.fixture
    def church_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def member_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        user.is_superuser = False
        return user
    
    def test_is_church_returns_true_for_church_role(self, church_user):
       
        assert is_church(church_user) is True
    
    def test_is_church_returns_false_for_member_role(self, member_user):
        assert is_church(member_user) is False
    
    def test_is_member_returns_true_for_member_role(self, member_user):
        assert is_member(member_user) is True
    
    def test_is_member_returns_false_for_church_role(self, church_user):
        assert is_member(church_user) is False
    
    def test_is_admin_returns_true_for_admin_role(self, admin_user):
        assert is_admin(admin_user) is True
    
    def test_is_admin_returns_true_for_superuser(self, superuser):
        assert is_admin(superuser) is True
    
    def test_is_admin_returns_false_for_regular_user(self, member_user):
        assert is_admin(member_user) is False
    
    def test_is_superuser_returns_true_for_superuser(self, superuser):
        assert is_superuser(superuser) is True
    
    def test_is_superuser_returns_false_for_admin(self, admin_user):
        assert is_superuser(admin_user) is False


class TestUserStatusChecks:
    """Testes para verificações de status do usuário."""
    @pytest.fixture
    def member_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        user.is_superuser = False
        user.is_staff = False
        return user
    
    @pytest.fixture
    def active_verified_user(self):
        user = Mock(spec=User)
        user.is_active = True
        user.is_trusty = True
        return user
    
    @pytest.fixture
    def inactive_user(self):
        user = Mock(spec=User)
        user.is_active = False
        user.is_trusty = True
        return user
    
    @pytest.fixture
    def unverified_user(self):
        user = Mock(spec=User)
        user.is_active = True
        user.is_trusty = False
        return user
    
    def test_is_active_returns_true_for_active_user(self, active_verified_user):
        assert is_active(active_verified_user) is True
    
    def test_is_active_returns_false_for_inactive_user(self, inactive_user):
        assert is_active(inactive_user) is False
    
    def test_is_trusty_returns_true_for_verified_user(self, active_verified_user):
        assert is_trusty(active_verified_user) is True
    
    def test_is_trusty_returns_false_for_unverified_user(self, unverified_user):
        assert is_trusty(unverified_user) is False
    
    def test_is_verified_returns_true_when_active_and_trusty(self, active_verified_user):
        assert is_verified(active_verified_user) is True
    
    def test_is_verified_returns_false_when_inactive(self, inactive_user):
        assert is_verified(inactive_user) is False
    
    def test_is_verified_returns_false_when_untrusty(self, unverified_user):
        assert is_verified(unverified_user) is False
    
    def test_is_staff_returns_true_for_staff_user(self):
        user = Mock(spec=User)
        user.is_staff = True
        assert is_staff(user) is True
    
    def test_is_staff_returns_false_for_non_staff_user(self, member_user):
        member_user.is_staff = False
        assert is_staff(member_user) is False


class TestChurchMembershipChecks:
    """Testes para verificações de vínculo com igreja."""
    @pytest.fixture
    def church_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def church(self):
        return Mock(spec=Church)
    
    @pytest.fixture
    def member_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.ADMIN
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def member_with_church_membership(self, member_user, church):
        membership = Mock(spec=MemberChurch)
        membership.role = MemberChurch.Role.PASTOR
        membership.status = MemberChurch.Status.ACTIVE
        
        member = Mock()
        member.church_memberships = Mock()
        member.church_memberships.get.return_value = membership
        mock_queryset = Mock()
        mock_queryset.exists.return_value = True
        member.church_memberships.filter.return_value = mock_queryset
        
        member_user.member = member
        return member_user
    
    @patch('ecclesia.apps.users.permissions.roles.is_admin')
    def test_has_role_in_church_returns_true_for_admin(self, mock_is_admin, admin_user, church):
        mock_is_admin.return_value = True
        
        result = has_role_in_church(admin_user, church, MemberChurch.Role.PASTOR)
        assert result is True
    
    def test_has_role_in_church_returns_false_for_non_member(self, church_user, church):
        # Church user não é membro
        result = has_role_in_church(church_user, church, MemberChurch.Role.PASTOR)
        assert result is False
    
    def test_has_role_in_church_returns_true_for_correct_role(self, member_with_church_membership, church):
        result = has_role_in_church(
            member_with_church_membership, 
            church, 
            MemberChurch.Role.PASTOR
        )
        assert result is True
    
    def test_has_role_in_church_returns_false_for_wrong_role(self, member_with_church_membership, church):
        result = has_role_in_church(
            member_with_church_membership, 
            church, 
            MemberChurch.Role.TREASURER
        )
        assert result is False
    
    def test_has_role_in_church_returns_false_when_membership_not_found(self, member_user, church):
        member_user.member.church_memberships.get.side_effect = Exception("Not found")
        
        result = has_role_in_church(member_user, church, MemberChurch.Role.PASTOR)
        assert result is False
    
    @patch('ecclesia.apps.users.permissions.roles.has_role_in_church')
    def test_is_church_admin_calls_has_role_in_church_with_correct_role(self, mock_has_role, member_user, church):
        is_church_admin(member_user, church)
        mock_has_role.assert_called_with(member_user, church, MemberChurch.Role.CHURCH_ADMIN)
    
    @patch('ecclesia.apps.users.permissions.roles.has_role_in_church')
    def test_is_pastor_calls_has_role_in_church_with_correct_role(self, mock_has_role, member_user, church):
        is_pastor(member_user, church)
        mock_has_role.assert_called_with(member_user, church, MemberChurch.Role.PASTOR)
    
    @patch('ecclesia.apps.users.permissions.roles.has_role_in_church')
    def test_is_treasurer_calls_has_role_in_church_with_correct_role(self, mock_has_role, member_user, church):
        is_treasurer(member_user, church)
        mock_has_role.assert_called_with(member_user, church, MemberChurch.Role.TREASURER)
    
    @patch('ecclesia.apps.users.permissions.roles.has_role_in_church')
    def test_is_secretary_calls_has_role_in_church_with_correct_role(self, mock_has_role, member_user, church):
        is_secretary(member_user, church)
        mock_has_role.assert_called_with(member_user, church, MemberChurch.Role.SECRETARY)
    
    @patch('ecclesia.apps.users.permissions.roles.is_admin')
    def test_is_member_of_church_returns_true_for_admin(self, mock_is_admin, admin_user, church):
        mock_is_admin.return_value = True
        
        result = is_member_of_church(admin_user, church)
        assert result is True
    
    def test_is_member_of_church_returns_false_for_church_user(self, church_user, church):
        result = is_member_of_church(church_user, church)
        assert result is False
    
    def test_is_member_of_church_returns_true_when_membership_exists(self, member_with_church_membership, church):
        result = is_member_of_church(member_with_church_membership, church)
        assert result is True
    
    def test_is_member_of_church_returns_false_when_no_membership(self, member_user, church):
        member_user.member.church_memberships.filter.return_value.exists.return_value = False
        
        result = is_member_of_church(member_user, church)
        assert result is False


class TestOwnershipChecks:
    """Testes para verificações de ownership."""
    
    @pytest.fixture
    def user(self):
        user = Mock(spec=User)
        user.id = "123"
        return user
    
    @pytest.fixture
    def other_user(self):
        user = Mock(spec=User)
        user.id = "456"
        return user
    
    @pytest.fixture
    def church(self, user):
        church = Mock(spec=Church)
        church.user = user
        return church
    
    @pytest.fixture
    def member(self, user):
        member = Mock()
        member.user = user
        return member
    
    def test_is_owner_returns_true_for_same_user_id(self, user):
        assert is_owner(user, user.id) is True
    
    def test_is_owner_returns_false_for_different_user_id(self, user, other_user):
        assert is_owner(user, other_user.id) is False
    
    def test_is_church_owner_returns_true_for_church_owner(self, user, church):
        assert is_church_owner(user, church) is True
    
    def test_is_church_owner_returns_false_for_non_owner(self, other_user, church):
        assert is_church_owner(other_user, church) is False
    
    def test_is_member_owner_returns_true_for_member_owner(self, user, member):
        assert is_member_owner(user, member) is True
    
    def test_is_member_owner_returns_false_for_non_owner(self, other_user, member):
        assert is_member_owner(other_user, member) is False


class TestCombinators:
    """Testes para funções combinadoras."""
    
    @pytest.fixture
    def user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        return user
    
    @pytest.fixture
    def church(self):
        return Mock(spec=Church)
        
    def test_has_any_role_returns_true_for_matching_role(self, user):
        roles = [User.UserRole.CHURCH, User.UserRole.MEMBER]
        assert has_any_role(user, roles) is True
    
    def test_has_any_role_returns_false_for_non_matching_role(self, user):
        roles = [User.UserRole.CHURCH, User.UserRole.ADMIN]
        assert has_any_role(user, roles) is False
    
    def test_has_all_roles_returns_true_for_all_matching(self, user):
        roles = [User.UserRole.MEMBER]
        assert has_all_roles(user, roles) is True
    
    def test_has_all_roles_returns_false_for_not_all_matching(self, user):
        roles = [User.UserRole.MEMBER, User.UserRole.CHURCH]
        assert has_all_roles(user, roles) is False
    
    @patch('ecclesia.apps.users.permissions.roles.is_admin')
    @patch('ecclesia.apps.users.permissions.roles.is_church_owner')
    @patch('ecclesia.apps.users.permissions.roles.is_church_admin')
    @patch('ecclesia.apps.users.permissions.roles.is_pastor')
    @patch('ecclesia.apps.users.permissions.roles.is_treasurer')
    @patch('ecclesia.apps.users.permissions.roles.is_secretary')
    def test_can_manage_church_returns_true_for_admin(
        self, mock_secretary, mock_treasurer, mock_pastor, 
        mock_admin, mock_owner, mock_is_admin, user, church
    ):
        mock_is_admin.return_value = True
        
        result = can_manage_church(user, church)
        assert result is True
    
    @patch('ecclesia.apps.users.permissions.roles.is_admin')
    @patch('ecclesia.apps.users.permissions.roles.is_church_owner')
    def test_can_manage_church_returns_true_for_owner(self, mock_owner, mock_is_admin, user, church):
        mock_is_admin.return_value = False
        mock_owner.return_value = True
        
        result = can_manage_church(user, church)
        assert result is True
    
    @patch('ecclesia.apps.users.permissions.roles.is_admin')
    @patch('ecclesia.apps.users.permissions.roles.is_church_owner')
    @patch('ecclesia.apps.users.permissions.roles.is_pastor')
    def test_can_view_finances_returns_true_for_pastor(self, mock_pastor, mock_owner, mock_is_admin, user, church):
        mock_is_admin.return_value = False
        mock_owner.return_value = False
        mock_pastor.return_value = True
        
        result = can_view_finances(user, church)
        assert result is True
    
    @patch('ecclesia.apps.users.permissions.roles.is_admin')
    @patch('ecclesia.apps.users.permissions.roles.is_church_owner')
    @patch('ecclesia.apps.users.permissions.roles.is_pastor')
    @patch('ecclesia.apps.users.permissions.roles.is_treasurer')
    @patch('ecclesia.apps.users.permissions.roles.is_church_admin')
    def test_can_view_finances_returns_false_for_member(
        self, mock_admin, mock_treasurer, mock_pastor, 
        mock_owner, mock_is_admin, user, church
    ):
    
        mock_is_admin.return_value = False
        mock_owner.return_value = False
        mock_pastor.return_value = False
        mock_treasurer.return_value = False
        mock_admin.return_value = False
        
        result = can_view_finances(user, church)
        assert result is False
    