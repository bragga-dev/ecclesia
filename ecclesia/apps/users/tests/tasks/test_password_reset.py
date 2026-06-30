"""
Testes para a task send_password_reset_email.
"""
import uuid
from unittest.mock import patch, MagicMock

import pytest
from celery.exceptions import Retry
from django.conf import settings
from django.utils.html import strip_tags
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.tasks.password_reset import send_password_reset_email


@pytest.mark.django_db
class TestSendPasswordResetEmail:
    """Testes para a task de redefinição de senha."""

    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.user = User.objects.create_user(
            email="reset@example.com",
            password="test123"
        )
        self.uid = "dGVzdC11aWQ"
        self.token = "test-token"

    @patch('ecclesia.apps.users.tasks.password_reset.TokenService')
    @patch('ecclesia.apps.users.tasks.password_reset.EmailService')
    @patch('ecclesia.apps.users.tasks.password_reset.logger')
    def test_send_password_reset_email_success(self, mock_logger, mock_email_service, mock_token_service):
        """Testa envio de e-mail de redefinição de senha com sucesso."""
        # Configurar mock
        mock_token_service.build_password_reset_url.return_value = (
            f"{settings.FRONTEND_URL}/redefinir-senha/{self.uid}/{self.token}"
        )

        send_password_reset_email(self.user.id, self.uid, self.token)

        # Verificar se TokenService foi chamado corretamente
        mock_token_service.build_password_reset_url.assert_called_once_with(self.uid, self.token)

        # Verificar se EmailService foi chamado corretamente
        mock_email_service.send_html_email.assert_called_once()
        call_args = mock_email_service.send_html_email.call_args[1]
        assert call_args["subject"] == "Redefinição de senha — Ecclesia"
        assert call_args["to_email"] == self.user.email
        assert call_args["template_name"] == "users/emails/password_reset.html"
        assert call_args["context"]["user_email"] == self.user.email
        assert call_args["context"]["reset_url"] == mock_token_service.build_password_reset_url.return_value

        # Verificar logs
        mock_logger.info.assert_any_call(
            "Password reset URL generated: %s",
            mock_token_service.build_password_reset_url.return_value
        )
        mock_logger.info.assert_any_call(
            "Password reset email sent to %s",
            self.user.email
        )

    def test_send_password_reset_email_user_not_found(self):
        """Testa comportamento quando usuário não é encontrado."""
        with patch.object(User.objects, "get", side_effect=User.DoesNotExist):
            with patch.object(send_password_reset_email, 'retry', side_effect=Retry()):
                with pytest.raises(Retry):
                    send_password_reset_email(str(uuid.uuid4()), self.uid, self.token)

    @patch('ecclesia.apps.users.tasks.password_reset.TokenService')
    @patch('ecclesia.apps.users.tasks.password_reset.EmailService')
    @patch('ecclesia.apps.users.tasks.password_reset.logger')
    def test_send_password_reset_email_retry_on_failure(self, mock_logger, mock_email_service, mock_token_service):
        """Testa que a task tenta novamente em caso de falha no envio."""
        # Configurar mock
        mock_token_service.build_password_reset_url.return_value = (
            f"{settings.FRONTEND_URL}/redefinir-senha/{self.uid}/{self.token}"
        )
        
        # Simular falha no envio do email
        mock_email_service.send_html_email.side_effect = Exception("SMTP error")

        # Mockar o método retry da task
        with patch.object(send_password_reset_email, 'retry', side_effect=Retry()):
            with pytest.raises(Retry):
                send_password_reset_email(self.user.id, self.uid, self.token)

            mock_logger.exception.assert_called_once()
            assert "Error sending password reset email" in mock_logger.exception.call_args[0][0]