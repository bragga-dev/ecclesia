"""
Testes para a task send_affiliation_offline_invite.
"""
import uuid
from unittest.mock import patch, MagicMock
import pytest
from celery.exceptions import Retry
from django.conf import settings

from ecclesia.apps.community.tasks.send_affiliation_offline_invite import (
    send_affiliation_offline_invite,
)


@pytest.mark.django_db
class TestSendAffiliationOfflineInvite:
    """Testes para a task de convite offline de afiliação."""

    def setup_method(self):
        """Configuração inicial para cada teste."""
        self.church_affiliation_id = uuid.uuid4()
        self.from_church_name = "Igreja Teste"
        self.invited_email = "convidado@exemplo.com"
        self.invited_church_full_name = "Igreja Convidada"

    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.get_church_affiliation_request_by_id')
    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.EmailService')
    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.logger')
    def test_send_affiliation_offline_invite_success(
        self, mock_logger, mock_email_service, mock_get_affiliation
    ):
        """Testa envio de convite offline com sucesso."""
        # Mock da afiliação
        mock_affiliation = self._create_mock_affiliation_offline()
        mock_get_affiliation.return_value = mock_affiliation

        # Executar task
        send_affiliation_offline_invite(self.church_affiliation_id)

        # Verificar se get foi chamado com o ID correto
        mock_get_affiliation.assert_called_once_with(self.church_affiliation_id)

        # Verificar se EmailService foi chamado
        mock_email_service.send_html_email.assert_called_once()
        call_args = mock_email_service.send_html_email.call_args[1]
        
        assert call_args["subject"] == "Nova Solicitação de Afiliação"
        assert call_args["to_email"] == self.invited_email
        assert call_args["template_name"] == "community/emails/affiliation_offline_invite.html"
        assert call_args["context"]["from_church_name"] == self.from_church_name
        assert call_args["context"]["invitation_url"] == (
            f"{settings.FRONTEND_URL}/dashboard/community/affiliations/{mock_affiliation.code}"
        )

        # Verificar logs
        mock_logger.info.assert_called_once()
        assert "Affiliation invite email sent" in mock_logger.info.call_args[0][0]

    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.get_church_affiliation_request_by_id')
    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.logger')
    def test_send_affiliation_offline_invite_not_found(
        self, mock_logger, mock_get_affiliation
    ):
        """Testa comportamento quando afiliação não é encontrada."""
        mock_get_affiliation.return_value = None

        send_affiliation_offline_invite(self.church_affiliation_id)

        mock_get_affiliation.assert_called_once_with(self.church_affiliation_id)
        mock_logger.warning.assert_called_once()
        assert "Affiliation %s not found" in mock_logger.warning.call_args[0][0]
        mock_email_service = None  # EmailService não deve ser chamado

    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.get_church_affiliation_request_by_id')
    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.EmailService')
    @patch('ecclesia.apps.community.tasks.send_affiliation_offline_invite.logger')
    def test_send_affiliation_offline_invite_retry_on_failure(
        self, mock_logger, mock_email_service, mock_get_affiliation
    ):
        """Testa que a task tenta novamente em caso de falha."""
        # Mock da afiliação
        mock_affiliation = self._create_mock_affiliation_offline()
        mock_get_affiliation.return_value = mock_affiliation

        # Simular falha no envio do email
        mock_email_service.send_html_email.side_effect = Exception("SMTP error")

        # Mockar o método retry da task
        with patch.object(send_affiliation_offline_invite, 'retry', side_effect=Retry()):
            with pytest.raises(Retry):
                send_affiliation_offline_invite(self.church_affiliation_id)

            mock_logger.exception.assert_called_once()
            assert "Error sending affiliation invite email" in mock_logger.exception.call_args[0][0]

    def _create_mock_affiliation_offline(self):
        """Cria um mock de afiliação offline."""
        mock_affiliation = MagicMock()
        mock_affiliation.id = self.church_affiliation_id
        mock_affiliation.code = "ABC123"
        mock_affiliation.invited_email = self.invited_email
        mock_affiliation.invited_church_full_name = self.invited_church_full_name
        mock_affiliation.message = "Mensagem de convite"
        mock_affiliation.created_at = "2024-01-01"
        mock_affiliation.expires_at = "2024-02-01"

        # Mock da igreja que está convidando
        mock_affiliation.from_church = MagicMock()
        mock_affiliation.from_church.id = uuid.uuid4()
        mock_affiliation.from_church.full_name = self.from_church_name
        mock_affiliation.from_church.user = MagicMock()
        mock_affiliation.from_church.user.email = "igreja@teste.com"
        mock_affiliation.from_church.get_church_type_display.return_value = "Matriz"
        mock_affiliation.from_church.cnpj = "12.345.678/0001-90"
        mock_affiliation.from_church.website = "https://igreja.com"
        mock_affiliation.from_church.instagram = "@igreja"
        mock_affiliation.from_church.about = "Sobre a igreja"
        mock_affiliation.from_church.phone = "+5511999998888"
        mock_affiliation.from_church.banner_url = "https://igreja.com/banner.jpg"

        return mock_affiliation