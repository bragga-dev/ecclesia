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
def send_affiliation_cancelled_to_parish(self, church_affiliation_id: uuid.UUID,) -> None:
    """
    Notifica a Sede (from_church) de que o convite foi cancelado.

    Envia para o e-mail da Sede:
      - Nome da igreja que cancelou
      - Link para visualizar a afiliação no dashboard
    """
    try:
        affiliation = get_church_affiliation_request_by_id(church_affiliation_id)

        if not affiliation:
            logger.warning("Affiliation %s not found", church_affiliation_id)
            return

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        affiliation_url = f"{frontend_url}/dashboard/community/affiliations"

        cancelled_church_name = (affiliation.to_church.full_name if affiliation.to_church else affiliation.invited_church_full_name) or ""

        context = {
            "parish_name": affiliation.from_church.full_name or "",
            "cancelled_church_name": cancelled_church_name,
            "affiliation_url": affiliation_url,
            "accepted_at": affiliation.accepted_at,
            "mode": affiliation.get_mode_display(),
        }

        EmailService.send_html_email(
            subject=f"Convite cancelado — {cancelled_church_name} não faz mais parte da sua rede",
            to_email=affiliation.to_church.user.email if affiliation.to_church else affiliation.invited_email,
            template_name="community/emails/affiliation_cancelled_to_parish.html",
            context=context,
        )

        logger.info(
            "Affiliation cancelled notification sent to parish. "
            "request_id=%s parish=%s cancelled_by=%s",
            affiliation.id,
            affiliation.from_church.id,
            cancelled_church_name,
        )

    except Exception as exc:
        logger.exception("Error sending affiliation cancelled notification. request_id=%s", church_affiliation_id,)
        raise self.retry(exc=exc)