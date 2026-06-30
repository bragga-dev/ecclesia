"""
Testes para a task send_verification_email.
"""
import uuid
from unittest.mock import patch, MagicMock
from django.conf import settings
import pytest
from celery.exceptions import Retry

from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.tasks.verification import send_verification_email


@pytest.mark.django_db
class TestSendVerificationEmail:
    """Testes para a task de verificação de e-mail."""

    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="test123"
        )

    @patch('ecclesia.apps.users.tasks.verification.TokenService')
    @patch('ecclesia.apps.users.tasks.verification.EmailService')
    @patch('ecclesia.apps.users.tasks.verification.logger')
    def test_send_verification_email_success(self, mock_logger, mock_email_service, mock_token_service):
        """Testa envio de e-mail de verificação com sucesso."""
        # Configurar mocks
        mock_token_service.generate_verification_data.return_value = ("dGVzdC11aWQ=", "test-token")
        mock_token_service.build_verification_url.return_value = (
            f"{settings.BACKEND_URL}/api/users/verify-email/dGVzdC11aWQ=/test-token"
        )

        send_verification_email(self.user.id)

        # Verificar se TokenService foi chamado corretamente
        mock_token_service.generate_verification_data.assert_called_once_with(self.user)
        mock_token_service.build_verification_url.assert_called_once_with("dGVzdC11aWQ=", "test-token")

        # Verificar se EmailService foi chamado corretamente
        mock_email_service.send_html_email.assert_called_once()
        call_args = mock_email_service.send_html_email.call_args[1]
        assert call_args["subject"] == "Confirme seu e-mail — Ecclesia"
        assert call_args["to_email"] == self.user.email
        assert call_args["template_name"] == "users/emails/verification_email.html"
        assert call_args["context"]["user_email"] == self.user.email
        assert call_args["context"]["verify_url"] == mock_token_service.build_verification_url.return_value

        # Verificar logs
        mock_logger.info.assert_any_call(
            "Verification URL generated: %s",
            mock_token_service.build_verification_url.return_value
        )
        mock_logger.info.assert_any_call(
            "Verification email sent to %s",
            self.user.email
        )

    @patch('ecclesia.apps.users.tasks.verification.User.objects.get')
    @patch('ecclesia.apps.users.tasks.verification.logger')
    def test_send_verification_email_user_not_found(self, mock_logger, mock_user_get):
        """Testa comportamento quando usuário não é encontrado."""
        mock_user_get.side_effect = User.DoesNotExist

        with pytest.raises(User.DoesNotExist):
            send_verification_email(uuid.uuid4())

        mock_logger.exception.assert_called_once()
        assert "Error sending verification email" in mock_logger.exception.call_args[0][0]

    @patch('ecclesia.apps.users.tasks.verification.TokenService')
    @patch('ecclesia.apps.users.tasks.verification.EmailService')
    @patch('ecclesia.apps.users.tasks.verification.logger')
    def test_send_verification_email_retry_on_failure(self, mock_logger, mock_email_service, mock_token_service):
        """Testa que a task tenta novamente em caso de falha no envio."""
        # Configurar mocks
        mock_token_service.generate_verification_data.return_value = ("dGVzdC11aWQ=", "test-token")
        mock_token_service.build_verification_url.return_value = (
            f"{settings.BACKEND_URL}/api/users/verify-email/dGVzdC11aWQ=/test-token"
        )
        
        # Simular falha no envio do email
        mock_email_service.send_html_email.side_effect = Exception("SMTP error")

        # Mockar o método retry da task
        with patch.object(send_verification_email, 'retry', side_effect=Retry()):
            with pytest.raises(Retry):
                send_verification_email(self.user.id)

            mock_logger.exception.assert_called_once()
            assert "Error sending verification email" in mock_logger.exception.call_args[0][0]