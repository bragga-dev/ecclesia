# tests/tasks/test_member_invite.py
"""
Testes para a task send_member_invite_email.
"""
import uuid
from unittest.mock import patch, MagicMock

import pytest
from django.conf import settings
from django.utils.html import strip_tags
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

    @patch('ecclesia.apps.users.tasks.member_invite.render_to_string')
    @patch('ecclesia.apps.users.tasks.member_invite.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_success(self, mock_logger, mock_email_class, mock_render):
        """Testa envio de e-mail de convite de membro com sucesso."""
        mock_render.return_value = "<html>Invite email content</html>"

        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        send_member_invite_email(self.member_user.id, self.temp_password, self.church_id)

        mock_render.assert_called_once()
        template_name = mock_render.call_args[0][0]
        assert template_name == "users/emails/member_invite.html"

        call_args = mock_render.call_args[0][1]
        assert set(call_args.keys()) == {
            "member_email", "temp_password", "verify_url", "church_name", "church_banner"
        }
        assert call_args["member_email"] == self.member_user.email
        assert call_args["temp_password"] == self.temp_password
        assert call_args["church_name"] == self.church.full_name
        assert call_args["church_banner"] == self.church.banner_url
        assert call_args["verify_url"].startswith(
            f"{settings.BACKEND_URL}/api/users/verify-email/"
        )

        expected_text_body = strip_tags(mock_render.return_value)
        mock_email_class.assert_called_once_with(
            subject="Bem-vindo à Ecclesia — Confirme seu e-mail",
            body=expected_text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.member_user.email],
        )

        mock_email_instance.attach_alternative.assert_called_once_with(
            mock_render.return_value, "text/html"
        )

        mock_email_instance.send.assert_called_once_with(fail_silently=False)

        mock_logger.info.assert_any_call("Member invite email sent to %s", self.member_user.email)

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

    @patch('ecclesia.apps.users.tasks.member_invite.render_to_string')
    @patch('ecclesia.apps.users.tasks.member_invite.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_retry_on_failure(self, mock_logger, mock_email_class, mock_render):
        """Testa que a task propaga a falha de envio (acionando retry do Celery)."""
        mock_render.return_value = "<html>Invite email content</html>"

        mock_email_instance = MagicMock()
        mock_email_instance.send.side_effect = Exception("SMTP error")
        mock_email_class.return_value = mock_email_instance

        with pytest.raises(Exception, match="SMTP error"):
            send_member_invite_email(self.member_user.id, self.temp_password, self.church_id)

        mock_logger.exception.assert_called_once()
        assert "Error sending member invite email" in mock_logger.exception.call_args[0][0]

    @patch('ecclesia.apps.users.tasks.member_invite.logger')
    def test_send_member_invite_email_logs_url(self, mock_logger):
        """Testa que a URL de verificação é logada corretamente."""
        # MOCKAR O TOKEN GENERATOR E UID ANTES DE CHAMAR A FUNÇÃO
        with patch('ecclesia.apps.users.tasks.member_invite.default_token_generator') as mock_gen:
            mock_gen.make_token.return_value = "test-token"
            with patch('ecclesia.apps.users.tasks.member_invite.urlsafe_base64_encode') as mock_uid:
                mock_uid.return_value = "dGVzdC11aWQ="
                with patch('ecclesia.apps.users.tasks.member_invite.render_to_string') as mock_render:
                    mock_render.return_value = "<html>content</html>"
                    with patch('ecclesia.apps.users.tasks.member_invite.EmailMultiAlternatives') as mock_email:
                        mock_email_instance = MagicMock()
                        mock_email.return_value = mock_email_instance

                        send_member_invite_email(self.member_user.id, self.temp_password, self.church_id)

                        expected_url = f"{settings.BACKEND_URL}/api/users/verify-email/dGVzdC11aWQ=/test-token"
                        mock_logger.info.assert_any_call("Member invite URL generated: %s", expected_url)