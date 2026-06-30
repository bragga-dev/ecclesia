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

    @patch("ecclesia.apps.users.tasks.password_reset.render_to_string")
    @patch("ecclesia.apps.users.tasks.password_reset.EmailMultiAlternatives")
    @patch("ecclesia.apps.users.tasks.password_reset.logger")
    def test_send_password_reset_email_success(self, mock_logger, mock_email_class, mock_render):
        """Testa envio de e-mail de redefinição de senha com sucesso."""
        html_content = "<html>Reset email content</html>"
        mock_render.return_value = html_content

        mock_email_instance = MagicMock()
        mock_email_class.return_value = mock_email_instance

        send_password_reset_email(self.user.id, self.uid, self.token)

        template_name = mock_render.call_args[0][0]
        assert template_name == "users/emails/password_reset.html"

        context = mock_render.call_args[0][1]
        assert context["user_email"] == self.user.email
        assert context["reset_url"] == (
            f"{settings.FRONTEND_URL}/redefinir-senha/{self.uid}/{self.token}"
        )

        expected_text_body = strip_tags(html_content)
        mock_email_class.assert_called_once_with(
            subject="Redefinição de senha — Ecclesia",
            body=expected_text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[self.user.email],
        )

        mock_email_instance.attach_alternative.assert_called_once_with(
            html_content, "text/html"
        )
        mock_email_instance.send.assert_called_once_with(fail_silently=False)

        mock_logger.info.assert_any_call(
            "Password reset URL generated: %s",
            f"{settings.FRONTEND_URL}/redefinir-senha/{self.uid}/{self.token}"
        )
        mock_logger.info.assert_any_call(
            "Password reset email sent to %s",
            self.user.email
        )

    def test_send_password_reset_email_user_not_found(self):
        """Testa comportamento quando usuário não é encontrado."""
        # Mock o método retry para levantar Retry imediatamente
        with patch.object(send_password_reset_email, 'retry', side_effect=Retry()):
            with patch.object(User.objects, "get", side_effect=User.DoesNotExist):
                with pytest.raises(Retry):
                    send_password_reset_email(str(uuid.uuid4()), self.uid, self.token)

    @patch("ecclesia.apps.users.tasks.password_reset.logger")
    @patch("ecclesia.apps.users.tasks.password_reset.render_to_string")
    @patch("ecclesia.apps.users.tasks.password_reset.EmailMultiAlternatives")
    def test_send_password_reset_email_retry_on_failure(self, mock_email_class, mock_render, mock_logger):
        """Testa que a task tenta novamente em caso de falha no envio."""
        # Mock o método retry para levantar Retry imediatamente
        with patch.object(send_password_reset_email, 'retry', side_effect=Retry()):
            with patch.object(User.objects, "get", return_value=self.user):
                mock_render.return_value = "<html>Reset email content</html>"

                mock_email_instance = MagicMock()
                mock_email_instance.send.side_effect = Exception("SMTP error")
                mock_email_class.return_value = mock_email_instance

                with pytest.raises(Retry):
                    send_password_reset_email(self.user.id, self.uid, self.token)

                mock_logger.exception.assert_called_once()
                assert "Error sending password reset email" in mock_logger.exception.call_args[0][0]