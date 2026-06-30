"""
Testes para a task send_member_invite_email.
"""
import uuid
from unittest.mock import patch, MagicMock

import pytest
from celery.exceptions import Retry
from django.conf import settings
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.models.church import Church
from ecclesia.apps.users.tasks.member_invite import send_member_invite_email


@pytest.mark.django_db
class TestSendMemberInviteEmail:
    """Testes para a task de convite de membro."""

    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.church_user = User.objects.create_user(
            email="igreja@teste.com",
            password="test123",
            role=User.UserRole.CHURCH
        )

        self.church = Church.objects.create(
            user=self.church_user,
            full_name="Igreja Teste",
            phone="+5511999998888",
        )

        self.member_user = User.objects.create_user(
            email="member@example.com",
            password="test123"
        )
        self.member_user.is_active = True
        self.member_user.save()

        self.temp_password = "TempPass123!"
        self.church_id = self.church.id

    @patch('ecclesia.apps.users.tasks.member_invite.TokenService')
    @patch('ecclesia.apps.users.tasks.member_invite.EmailService')
    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_success(self, mock_logger, mock_email_service, mock_token_service):
        """Testa envio de e-mail de convite de membro com sucesso."""
        # Configurar mocks
        mock_token_service.generate_verification_data.return_value = ("dGVzdC11aWQ=", "test-token")
        mock_token_service.build_verification_url.return_value = (
            f"{settings.BACKEND_URL}/api/users/verify-email/dGVzdC11aWQ=/test-token"
        )

        send_member_invite_email(self.member_user.id, self.temp_password, self.church_id)

        # Verificar se TokenService foi chamado corretamente
        mock_token_service.generate_verification_data.assert_called_once_with(self.member_user)
        mock_token_service.build_verification_url.assert_called_once_with("dGVzdC11aWQ=", "test-token")

        # Verificar se EmailService foi chamado corretamente
        mock_email_service.send_html_email.assert_called_once()
        call_args = mock_email_service.send_html_email.call_args[1]
        assert call_args["subject"] == "Bem-vindo à Ecclesia — Confirme seu e-mail"
        assert call_args["to_email"] == self.member_user.email
        assert call_args["template_name"] == "users/emails/member_invite.html"
        assert call_args["context"]["member_email"] == self.member_user.email
        assert call_args["context"]["temp_password"] == self.temp_password
        assert call_args["context"]["church_name"] == self.church.full_name
        assert call_args["context"]["church_banner"] == self.church.banner_url
        assert call_args["context"]["verify_url"] == mock_token_service.build_verification_url.return_value

        # Verificar logs
        mock_logger.info.assert_any_call(
            "Member invite URL generated: %s",
            mock_token_service.build_verification_url.return_value
        )
        mock_logger.info.assert_any_call(
            "Member invite email sent to %s",
            self.member_user.email
        )

    @patch('ecclesia.apps.users.models.user.User.objects.get')
    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_user_not_found(self, mock_logger, mock_user_get):
        """Testa comportamento quando usuário não é encontrado."""
        mock_user_get.side_effect = User.DoesNotExist

        with pytest.raises(User.DoesNotExist):
            send_member_invite_email(str(uuid.uuid4()), self.temp_password, self.church_id)

        mock_logger.exception.assert_called_once()
        assert "Error sending member invite email" in mock_logger.exception.call_args[0][0]

    @patch('ecclesia.apps.users.models.church.Church.objects.get')
    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_church_not_found(self, mock_logger, mock_church_get):
        """Testa comportamento quando igreja não é encontrada."""
        mock_church_get.side_effect = Church.DoesNotExist

        with pytest.raises(Church.DoesNotExist):
            send_member_invite_email(self.member_user.id, self.temp_password, uuid.uuid4())

        mock_logger.exception.assert_called_once()
        assert "Error sending member invite email" in mock_logger.exception.call_args[0][0]

    @patch('ecclesia.apps.users.tasks.member_invite.TokenService')
    @patch('ecclesia.apps.users.tasks.member_invite.EmailService')
    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_retry_on_failure(self, mock_logger, mock_email_service, mock_token_service):
        """Testa que a task tenta novamente em caso de falha no envio."""
        # Configurar mocks
        mock_token_service.generate_verification_data.return_value = ("dGVzdC11aWQ=", "test-token")
        mock_token_service.build_verification_url.return_value = (
            f"{settings.BACKEND_URL}/api/users/verify-email/dGVzdC11aWQ=/test-token"
        )
        
        # Simular falha no envio do email
        mock_email_service.send_html_email.side_effect = Exception("SMTP error")

        # Mockar o método retry da task
        with patch.object(send_member_invite_email, 'retry', side_effect=Retry()):
            with pytest.raises(Retry):
                send_member_invite_email(self.member_user.id, self.temp_password, self.church_id)

            mock_logger.exception.assert_called_once()
            assert "Error sending member invite email" in mock_logger.exception.call_args[0][0]

    @patch('ecclesia.apps.users.tasks.member_invite.TokenService')
    @patch('ecclesia.apps.users.tasks.member_invite.EmailService')
    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_logs_url(self, mock_logger, mock_email_service, mock_token_service):
        """Testa que a URL de verificação é logada corretamente."""
        # Configurar mocks
        mock_token_service.generate_verification_data.return_value = ("dGVzdC11aWQ=", "test-token")
        mock_token_service.build_verification_url.return_value = (
            f"{settings.BACKEND_URL}/api/users/verify-email/dGVzdC11aWQ=/test-token"
        )

        send_member_invite_email(self.member_user.id, self.temp_password, self.church_id)

        # Verificar se a URL foi logada
        mock_logger.info.assert_any_call(
            "Member invite URL generated: %s",
            mock_token_service.build_verification_url.return_value
        )