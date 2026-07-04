"""
Tasks Celery — Confirmação de aceite de convite offline.

Disparada após a nova igreja aceitar o convite.
Envia e-mail com:
  - Confirmação de que a conta foi criada e o vínculo estabelecido
  - Senha temporária gerada automaticamente
  - Instruções para alterar a senha
"""
import logging
import uuid

from celery import shared_task
from django.conf import settings
from ecclesia.apps.users.utils.email_service import EmailService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    default_retry_delay=60,
)
def send_affiliation_offline_accepted(
    self,
    church_affiliation_id: uuid.UUID,
    temp_password: str,
) -> None:
    """
    Envia e-mail de confirmação para a nova igreja após o aceite do convite.

    Contém:
      - Credenciais de acesso (email + senha temporária)
      - Confirmação do vínculo com a sede
      - Link do dashboard
      - Instrução para alterar a senha no primeiro acesso
    """
    try:
        from ecclesia.apps.community.selectors.church_in_church_selector import (
            get_church_affiliation_request_by_id,
        )

        affiliation = get_church_affiliation_request_by_id(church_affiliation_id)

        if not affiliation:
            logger.warning("Affiliation %s not found", church_affiliation_id)
            return

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        dashboard_url = f"{frontend_url}/dashboard"
        change_password_url = f"{frontend_url}/dashboard/settings/security"

        context = {
            # Nova igreja
            "church_name": affiliation.invited_church_full_name,
            "member_email": affiliation.invited_email,
            "temp_password": temp_password,
            # Sede remetente
            "from_church_name": affiliation.from_church.full_name,
            "church_banner": affiliation.from_church.banner_url,
            # Links
            "dashboard_url": dashboard_url,
            "change_password_url": change_password_url,
        }

        EmailService.send_html_email(
            subject="Bem-vindo à Ecclesia — Sua conta foi criada",
            to_email=affiliation.invited_email,
            template_name="community/emails/affiliation_offline_accepted.html",
            context=context,
        )


        logger.info(
            "Affiliation offline accepted email sent. request_id=%s to=%s",
            affiliation.id,
            affiliation.invited_email,
        )

    except Exception as exc:
        logger.exception(
            "Error sending affiliation offline accepted email. request_id=%s",
            church_affiliation_id,
        )
        raise self.retry(exc=exc)