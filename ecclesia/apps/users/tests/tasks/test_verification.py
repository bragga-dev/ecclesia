# tests/tasks/test_verification.py
"""
Testes para a task send_verification_email.
"""
import uuid
from unittest.mock import patch, MagicMock
from django.conf import settings
import pytest
from django.utils.html import strip_tags

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

    @patch('ecclesia.apps.users.tasks.verification.render_to_string')
    @patch('ecclesia.apps.users.tasks.verification.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.tasks.verification.logger')
    def test_send_verification_email_success(self, mock_logger, mock_email_class, mock_render):
        """Testa envio de e-mail de verificação com sucesso."""
        mock_render.return_value = "<html>Email content</html>"

        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        send_verification_email(self.user.id)

        mock_render.assert_called_once()
        template_name = mock_render.call_args[0][0]
        assert template_name == "users/emails/verification_email.html"

        call_args = mock_render.call_args[0][1]
        assert set(call_args.keys()) == {"user_email", "verify_url"}
        assert call_args["user_email"] == self.user.email
        assert call_args["verify_url"].startswith(
            f"{settings.BACKEND_URL}/api/users/verify-email/"
        )

        expected_text_body = strip_tags(mock_render.return_value)
        mock_email_class.assert_called_once_with(
            subject="Confirme seu e-mail — Ecclesia",
            body=expected_text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.user.email],
        )

        mock_email_instance.attach_alternative.assert_called_once_with(
            mock_render.return_value, "text/html"
        )

        mock_email_instance.send.assert_called_once_with(fail_silently=False)

        mock_logger.info.assert_called_once()
        assert "Verification email sent to" in mock_logger.info.call_args[0][0]
        assert mock_logger.info.call_args[0][1] == self.user.email

    @patch('ecclesia.apps.users.models.user.User.objects.get')
    @patch('ecclesia.apps.users.tasks.verification.logger')
    def test_send_verification_email_user_not_found(self, mock_logger, mock_user_get):
        """Testa comportamento quando usuário não é encontrado."""
        mock_user_get.side_effect = User.DoesNotExist

        with pytest.raises(User.DoesNotExist):
            send_verification_email(uuid.uuid4())

        mock_logger.exception.assert_called_once()
        assert "Error sending verification email" in mock_logger.exception.call_args[0][0]

    @patch('ecclesia.apps.users.tasks.verification.render_to_string')
    @patch('ecclesia.apps.users.tasks.verification.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.tasks.verification.logger')
    def test_send_verification_email_retry_on_failure(self, mock_logger, mock_email_class, mock_render):
        """Testa que a task propaga a falha de envio (acionando retry do Celery)."""
        mock_render.return_value = "<html>Email content</html>"

        mock_email_instance = MagicMock()
        mock_email_instance.send.side_effect = Exception("SMTP error")
        mock_email_class.return_value = mock_email_instance

        with pytest.raises(Exception, match="SMTP error"):
            send_verification_email(self.user.id)

        mock_logger.exception.assert_called_once()
        assert "Error sending verification email" in mock_logger.exception.call_args[0][0]

    @patch('ecclesia.apps.users.tasks.verification.render_to_string')
    @patch('ecclesia.apps.users.tasks.verification.EmailMultiAlternatives')
    @patch('ecclesia.apps.users.tasks.verification.logger')
    def test_send_verification_email_success(self, mock_logger, mock_email_class, mock_render):
        """Testa envio de e-mail de verificação com sucesso."""
        html_content = "<html>Email content</html>"
        mock_render.return_value = html_content

        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        send_verification_email(self.user.id)

        mock_render.assert_called_once()
        template_name = mock_render.call_args[0][0]
        assert template_name == "users/emails/verification_email.html"

        call_args = mock_render.call_args[0][1]
        assert set(call_args.keys()) == {"user_email", "verify_url"}
        assert call_args["user_email"] == self.user.email
        assert call_args["verify_url"].startswith(
            f"{settings.BACKEND_URL}/api/users/verify-email/"
        )

        expected_text_body = strip_tags(html_content)
        mock_email_class.assert_called_once_with(
            subject="Confirme seu e-mail — Ecclesia",
            body=expected_text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.user.email],
        )

        mock_email_instance.attach_alternative.assert_called_once_with(
            html_content, "text/html"
        )

        mock_email_instance.send.assert_called_once_with(fail_silently=False)

        # CORREÇÃO: Verificar que o logger foi chamado 2 vezes
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call(
            "Verification URL generated: %s",
            call_args["verify_url"]
        )
        mock_logger.info.assert_any_call(
            "Verification email sent to %s",
            self.user.email
        )