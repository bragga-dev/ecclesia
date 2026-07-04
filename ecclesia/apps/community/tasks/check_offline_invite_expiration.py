import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
import uuid
from ecclesia.apps.community.models import ChurchAffiliationRequest
from ecclesia.apps.community.tasks.send_affiliation_expired_to_parish import send_affiliation_expired_to_parish
from ecclesia.apps.community.selectors.church_in_church_selector import get_church_affiliation_request_by_id


logger = logging.getLogger(__name__)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    default_retry_delay=60,
    expires=300,  
)
def check_offline_invite_expiration(self, affiliation_id: uuid.UUID) -> None:
    """
    Verifica se um convite offline específico expirou e o cancela se necessário.
    Esta task é agendada individualmente para cada convite offline no momento da criação.
    """
    try:
        affiliation = get_church_affiliation_request_by_id(affiliation_id)

        if not affiliation:
            logger.warning("Affiliation %s not found for expiration check", affiliation_id)
            return

        if affiliation.status != ChurchAffiliationRequest.Status.PENDING:
            logger.info("Affiliation %s already processed (status: %s), skipping expiration", affiliation_id, affiliation.status)
            return

        if affiliation.is_expired():
            logger.info("Offline invite %s expired, canceling automatically", affiliation_id)
            affiliation.expire()
            send_affiliation_expired_to_parish.delay(affiliation_id)
            
            logger.info("Offline invite %s successfully canceled due to expiration",affiliation_id)
        else:
            logger.warning("Affiliation %s not expired yet (expires_at: %s), rescheduling", affiliation_id, affiliation.expires_at)
            check_offline_invite_expiration.apply_async(args=[affiliation_id], countdown=60)

    except Exception as exc:
        logger.exception("Error checking offline invite expiration for %s", affiliation_id)
        raise self.retry(exc=exc)