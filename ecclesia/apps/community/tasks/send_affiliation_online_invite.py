"""
Tasks Celery — Convite de afiliação entre igrejas.
"""

import logging
import uuid

from celery import shared_task

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ecclesia.apps.community.selectors.church_in_church_selector import (
    get_church_affiliation_request_by_id,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
    default_retry_delay=60,
)
def send_affiliation_online_invite(self, church_affiliation_id: uuid.UUID) -> None:
    """
    Envia email notificando uma igreja que recebeu
    um convite de afiliação.
    """

    try:

        affiliation = get_church_affiliation_request_by_id(church_affiliation_id)

        if not affiliation:
            logger.warning("Affiliation %s not found", church_affiliation_id,)
            return

        frontend_url = getattr(settings,"FRONTEND_URL", "http://localhost:5173",)

        invitation_url = (f"{frontend_url}/dashboard/community/affiliations/"f"{affiliation.id}")

        context = {
            "from_church_name": affiliation.from_church.full_name,
            "from_church_email": affiliation.from_church.user.email,
            "from_church_type": affiliation.from_church.get_church_type_display(),
            "from_church_cnpj": affiliation.from_church.cnpj,
            "from_church_website": affiliation.from_church.website,
            "from_church_instagram": affiliation.from_church.instagram,
            "from_church_about": affiliation.from_church.about,
            "message": affiliation.message,
            "from_church_phone":affiliation.from_church.phone,
            "request_id": affiliation.id,
            "created_at": affiliation.created_at,
            "banner_url": affiliation.from_church.banner_url,
            "invitation_url": invitation_url,
        }

        html_content = render_to_string("community/emails/affiliation_online_invite.html", context,)

        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject="Solicitação de Afiliação",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[affiliation.to_church.user.email,],
        )

        email.attach_alternative(html_content, "text/html",)

        email.send(fail_silently=False)

        logger.info("Affiliation invite email sent. ""request_id=%s from=%s to=%s", affiliation.id,
            affiliation.from_church.id, affiliation.invited_church_full_name,)

    except Exception as exc:
        logger.exception("Error sending affiliation invite email. ""request_id=%s", church_affiliation_id,)
        raise self.retry(exc=exc)