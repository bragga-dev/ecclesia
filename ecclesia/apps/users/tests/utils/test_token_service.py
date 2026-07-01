# tests/utils/test_tken_service.py (versão corrigida)
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from ecclesia.apps.users.utils.token_service import TokenService


class TestTokenService:
    
    @pytest.fixture
    def mock_user(self):
        """Cria um mock de usuário para testes."""
        user = Mock()
        user.pk = 1
        user.email = "test@example.com"
        # Adicionar atributos necessários para o token generator
        user.last_login = None
        user.password = "pbkdf2_sha256$..."
        return user
    
    @patch('ecclesia.apps.users.utils.token_service.default_token_generator')
    @patch('ecclesia.apps.users.utils.token_service.urlsafe_base64_encode')
    @patch('ecclesia.apps.users.utils.token_service.force_bytes')
    def test_generate_verification_data(self, mock_force_bytes, mock_urlsafe_base64_encode, mock_token_generator, mock_user):
        """Testa geração de dados de verificação."""
        # Configurar mocks
        mock_force_bytes.return_value = b'1'
        mock_urlsafe_base64_encode.return_value = 'MQ'
        mock_token_generator.make_token.return_value = 'abc123token'
        
        # Executar
        uid, token = TokenService.generate_verification_data(mock_user)
        
        # Verificações
        mock_force_bytes.assert_called_once_with(1)
        mock_urlsafe_base64_encode.assert_called_once_with(b'1')
        mock_token_generator.make_token.assert_called_once_with(mock_user)
        assert uid == 'MQ'
        assert token == 'abc123token'
    
    @patch('ecclesia.apps.users.utils.token_service.settings')
    def test_build_verification_url(self, mock_settings, mock_user):
        """Testa construção da URL de verificação."""
        mock_settings.BACKEND_URL = "https://api.example.com"
        
        uid = "MQ"
        token = "abc123token"
        
        expected_url = "https://api.example.com/api/users/verify-email/MQ/abc123token"
        result = TokenService.build_verification_url(uid, token)
        
        assert result == expected_url
    
    @patch('ecclesia.apps.users.utils.token_service.settings')
    def test_build_password_reset_url(self, mock_settings):
        """Testa construção da URL de redefinição de senha."""
        mock_settings.FRONTEND_URL = "https://frontend.example.com"
        
        uid = "MQ"
        token = "abc123token"
        
        expected_url = "https://frontend.example.com/redefinir-senha/MQ/abc123token"
        result = TokenService.build_password_reset_url(uid, token)
        
        assert result == expected_url
    
    def test_generate_verification_data_integration(self):
        """Teste de integração para geração de dados de verificação."""
        # Criar um usuário real ou um mock mais completo
      
        from ecclesia.apps.users.models.user import User 
        
        # Usar um usuário real do Django para o teste de integração
        user = User(
        
            email="test@example.com",
            password="pbkdf2_sha256$..."
        )
        user.pk = 1
        
        # Executar sem mocks (usando implementações reais)
        uid, token = TokenService.generate_verification_data(user)
        
        # Verificar formato do UID
        assert isinstance(uid, str)
        assert len(uid) > 0
        
        # Verificar formato do token
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verificar que o token é válido
        assert default_token_generator.check_token(user, token) is True
    
    def test_build_verification_url_integration(self):
        """Teste de integração para construção da URL de verificação."""
        uid = "MQ"
        token = "abc123token"
        
        result = TokenService.build_verification_url(uid, token)
        
        assert result.startswith("http")
        assert "/api/users/verify-email/" in result
        assert uid in result
        assert token in result
    
    def test_build_password_reset_url_integration(self):
        """Teste de integração para construção da URL de redefinição de senha."""
        uid = "MQ"
        token = "abc123token"
        
        result = TokenService.build_password_reset_url(uid, token)
        
        assert result.startswith("http")
        assert "/redefinir-senha/" in result
        assert uid in result
        assert token in result