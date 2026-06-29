# test_auth_classes.py
"""
Testes para as classes de autenticação.
"""
import pytest
from unittest.mock import Mock, patch
from ninja_jwt.authentication import JWTAuth
from ecclesia.apps.users.exceptions import PermissionDenied
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.models.church import Church
from ecclesia.apps.users.permissions.auth_classes import (
    ChurchOnlyAuth,
    AdminOnlyAuth,
    VerifiedUserAuth,
    MemberOnlyAuth,
    ChurchCompleteProfileAuth,
    ActiveUserAuth,

)


class TestChurchOnlyAuth:
    """Testes para ChurchOnlyAuth."""
    
    @pytest.fixture
    def church_only_auth(self):
        return ChurchOnlyAuth()
    
    @pytest.fixture
    def church_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        user.is_trusty = True  # Verificado
        return user
    
    @pytest.fixture
    def member_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        user.is_superuser = False
        user.is_trusty = True
        return user
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.ADMIN
        user.is_superuser = False
        user.is_trusty = True
        return user
    
    @pytest.fixture
    def unverified_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        user.is_trusty = False  # Não verificado
        user.is_active = True
        return user

    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_church_user(self, mock_super_auth, church_only_auth, church_user):
        mock_super_auth.return_value = church_user
        
        result = church_only_auth.authenticate(None, "token")
        assert result == church_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_admin_user(self, mock_super_auth, church_only_auth, admin_user):
        mock_super_auth.return_value = admin_user
        
        result = church_only_auth.authenticate(None, "token")
        assert result == admin_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_member_user(self, mock_super_auth, church_only_auth, member_user):
        mock_super_auth.return_value = member_user
        
        with pytest.raises(PermissionDenied) as exc_info:
            church_only_auth.authenticate(None, "token")
        
        assert "Apenas igrejas podem acessar este recurso" in str(exc_info.value)
    
   
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_returns_none_for_no_user(self, mock_super_auth, church_only_auth):
        mock_super_auth.return_value = None
        
        result = church_only_auth.authenticate(None, "token")
        assert result is None


class TestChurchCompleteProfileAuth:
    """Testes para ChurchCompleteProfileAuth."""
    
    @pytest.fixture
    def church_complete_auth(self):
        return ChurchCompleteProfileAuth()
    
    @pytest.fixture
    def church_with_complete_profile(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        user.photo = "custom/photo.jpg"
        
        church = Mock(spec=Church)
        church.full_name = "Igreja Teste"
        church.cnpj = "12345678901234"
        church.phone = "1199999999"
        church.banner = "custom/banner.jpg"
        church.about = "Descrição da igreja"
        church.instagram = "@igreja"
        church.user = user
        church.is_verified = True
        
        user.church = church
        return user
    
    @pytest.fixture
    def church_with_missing_fields(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        user.photo = "default/user_img.jpg"  # Foto padrão
        
        church = Mock(spec=Church)
        church.full_name = ""  # Campo vazio
        church.cnpj = None  # Campo nulo
        church.phone = "1199999999"
        church.banner = "default/banner.jpg"  # Banner padrão
        church.about = "Descrição"
        church.instagram = "@igreja"
        church.user = user
        church.is_verified = True
        
        user.church = church
        return user
    
    @pytest.fixture
    def church_without_church(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        user.church = None
        return user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_complete_profile(self, mock_super_auth, church_complete_auth, church_with_complete_profile):
        mock_super_auth.return_value = church_with_complete_profile
        
        result = church_complete_auth.authenticate(None, "token")
        assert result == church_with_complete_profile
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_missing_fields(self, mock_super_auth, church_complete_auth, church_with_missing_fields):
        mock_super_auth.return_value = church_with_missing_fields
        
        with pytest.raises(PermissionDenied) as exc_info:
            church_complete_auth.authenticate(None, "token")
        
        error_msg = str(exc_info.value)
        assert "Complete seu perfil" in error_msg
        assert "campo(s) obrigatório(s) faltando" in error_msg
        assert "Nome completo" in error_msg
        assert "CNPJ" in error_msg
        assert "Foto (não pode ser a foto padrão)" in error_msg
        assert "Banner (não pode ser a banner padrão)" in error_msg
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_unverified_church(self, mock_super_auth, church_complete_auth, church_with_complete_profile):
        church_with_complete_profile.church.is_verified = False
        mock_super_auth.return_value = church_with_complete_profile
        
        with pytest.raises(PermissionDenied) as exc_info:
            church_complete_auth.authenticate(None, "token")
        
        assert "igreja precisa ser verificada" in str(exc_info.value)
    
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_user_without_church(self, mock_super_auth, church_complete_auth):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        # Simula que user.church levanta DoesNotExist
        del user.church
        mock_super_auth.return_value = user
        
        with patch.object(Church, 'DoesNotExist', Exception):
            with pytest.raises(PermissionDenied) as exc_info:
                church_complete_auth.authenticate(None, "token")
            assert "Usuário não possui igreja vinculada" in str(exc_info.value)
        
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_non_church_user(self, mock_super_auth, church_complete_auth):
        member_user = Mock(spec=User)
        member_user.role = User.UserRole.MEMBER
        member_user.is_superuser = False
        mock_super_auth.return_value = member_user
        
        with pytest.raises(PermissionDenied) as exc_info:
            church_complete_auth.authenticate(None, "token")
        
        assert "Apenas igrejas podem acessar este recurso" in str(exc_info.value)


class TestMemberOnlyAuth:
    """Testes para MemberOnlyAuth."""
    
    @pytest.fixture
    def member_only_auth(self):
        return MemberOnlyAuth()
    
    @pytest.fixture
    def member_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        user.is_superuser = False
        user.is_trusty = True
        return user
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.ADMIN
        user.is_superuser = False
        user.is_trusty = True
        return user
    
    @pytest.fixture
    def church_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.CHURCH
        user.is_superuser = False
        user.is_trusty = True
        return user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_member_user(self, mock_super_auth, member_only_auth, member_user):
        mock_super_auth.return_value = member_user
        
        result = member_only_auth.authenticate(None, "token")
        assert result == member_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_admin_user(self, mock_super_auth, member_only_auth, admin_user):
        mock_super_auth.return_value = admin_user
        
        result = member_only_auth.authenticate(None, "token")
        assert result == admin_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_church_user(self, mock_super_auth, member_only_auth, church_user):
        mock_super_auth.return_value = church_user
        
        with pytest.raises(PermissionDenied) as exc_info:
            member_only_auth.authenticate(None, "token")
        
        assert "Apenas membros podem acessar este recurso" in str(exc_info.value)


class TestAdminOnlyAuth:
    """Testes para AdminOnlyAuth."""
    
    @pytest.fixture
    def admin_only_auth(self):
        return AdminOnlyAuth()
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.ADMIN
        return user
    
    @pytest.fixture
    def regular_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER
        return user
    
    @pytest.fixture
    def regular_user(self):
        user = Mock(spec=User)
        user.role = User.UserRole.MEMBER  # <-- ADICIONE ESTA LINHA
        user.is_superuser = False
        return user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_admin_user(self, mock_super_auth, admin_only_auth, admin_user):
        mock_super_auth.return_value = admin_user
        
        result = admin_only_auth.authenticate(None, "token")
        assert result == admin_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_regular_user(self, mock_super_auth, admin_only_auth, regular_user):
        mock_super_auth.return_value = regular_user
        
        with pytest.raises(PermissionDenied) as exc_info:
            admin_only_auth.authenticate(None, "token")
        
        assert "Apenas administradores podem acessar este recurso" in str(exc_info.value)


class TestActiveUserAuth:
    """Testes para ActiveUserAuth."""
    
    @pytest.fixture
    def active_user_auth(self):
        return ActiveUserAuth()
    
    @pytest.fixture
    def active_user(self):
        user = Mock(spec=User)
        user.is_active = True
        return user
    
    @pytest.fixture
    def inactive_user(self):
        user = Mock(spec=User)
        user.is_active = False
        return user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_active_user(self, mock_super_auth, active_user_auth, active_user):
        mock_super_auth.return_value = active_user
        
        result = active_user_auth.authenticate(None, "token")
        assert result == active_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_inactive_user(self, mock_super_auth, active_user_auth, inactive_user):
        mock_super_auth.return_value = inactive_user
        
        with pytest.raises(PermissionDenied) as exc_info:
            active_user_auth.authenticate(None, "token")
        
        assert "conta não está ativa" in str(exc_info.value)


class TestVerifiedUserAuth:
    """Testes para VerifiedUserAuth."""
    
    @pytest.fixture
    def verified_user_auth(self):
        return VerifiedUserAuth()
    
    @pytest.fixture
    def verified_user(self):
        user = Mock(spec=User)
        user.is_trusty = True
        user.is_active = True
        user.role = User.UserRole.MEMBER
        return user
    
    @pytest.fixture
    def admin_user(self):
        user = Mock(spec=User)
        user.is_trusty = False
        user.is_active = True
        user.role = User.UserRole.ADMIN
        user.is_superuser = False
        return user
    
    @pytest.fixture
    def unverified_user(self):
        user = Mock(spec=User)
        user.is_trusty = False  # Importante: não verificado
        user.is_active = True
        user.role = User.UserRole.MEMBER
        user.is_superuser = False  # Necessário: sem isso Mock retorna truthy, passando is_admin()
        return user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_verified_user(self, mock_super_auth, verified_user_auth, verified_user):
        mock_super_auth.return_value = verified_user
        
        result = verified_user_auth.authenticate(None, "token")
        assert result == verified_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_allows_admin_user(self, mock_super_auth, verified_user_auth, admin_user):
        mock_super_auth.return_value = admin_user
        
        result = verified_user_auth.authenticate(None, "token")
        assert result == admin_user
    
    @patch.object(JWTAuth, 'authenticate')
    def test_authenticate_denies_unverified_user(self, mock_super_auth, verified_user_auth, unverified_user):
        mock_super_auth.return_value = unverified_user
        
        with pytest.raises(PermissionDenied) as exc_info:
            verified_user_auth.authenticate(None, "token")
        
        assert "Verifique seu e-mail" in str(exc_info.value)