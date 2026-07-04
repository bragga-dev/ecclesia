"""
Tasks Celery — Notificação para a Sede quando convite é aceito.

Disparada após qualquer aceite de afiliação (online ou offline).
Notifica a Sede de que a nova igreja aceitou o convite.
"""
import logging
import uuid

from celery import shared_task
from django.conf import settings

from ecclesia.apps.community.selectors.church_in_church_selector import (
    get_church_affiliation_request_by_id,
)
from ecclesia.apps.users.utils.email_service import EmailService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    default_retry_delay=60,
)
def send_affiliation_accepted_to_parish(
    self,
    church_affiliation_id: uuid.UUID,
) -> None:
    """
    Notifica a Sede (from_church) de que o convite foi aceito.

    Envia para o e-mail da Sede:
      - Nome da igreja que aceitou
      - Link para visualizar a afiliação no dashboard
    """
    try:
        affiliation = get_church_affiliation_request_by_id(church_affiliation_id)

        if not affiliation:
            logger.warning("Affiliation %s not found", church_affiliation_id)
            return

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        affiliation_url = f"{frontend_url}/dashboard/community/affiliations"

        # Nome da igreja que aceitou — pode vir de to_church (online)
        # ou de invited_church_full_name (offline, antes de ter to_church)
        accepted_church_name = (
            affiliation.to_church.full_name
            if affiliation.to_church
            else affiliation.invited_church_full_name
        ) or ""

        context = {
            "parish_name": affiliation.from_church.full_name or "",
            "accepted_church_name": accepted_church_name,
            "affiliation_url": affiliation_url,
            "accepted_at": affiliation.accepted_at,
            "mode": affiliation.get_mode_display(),
        }

        EmailService.send_html_email(
            subject=f"Convite aceito — {accepted_church_name} agora faz parte da sua rede",
            to_email=affiliation.from_church.user.email,
            template_name="community/emails/affiliation_accepted_to_parish.html",
            context=context,
        )

        logger.info(
            "Affiliation accepted notification sent to parish. "
            "request_id=%s parish=%s accepted_by=%s",
            affiliation.id,
            affiliation.from_church.id,
            accepted_church_name,
        )

    except Exception as exc:
        logger.exception(
            "Error sending affiliation accepted notification. request_id=%s",
            church_affiliation_id,
        )
        raise self.retry(exc=exc)