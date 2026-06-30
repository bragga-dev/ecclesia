"""
Tasks Celery — verificação de email.
"""

from celery import shared_task
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import logging


logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_verification_email(self, user_id: str) -> None:
    """
    Envia e-mail de confirmação de conta.

    Gera:
    - uid seguro para URL
    - token do Django
    - e-mail HTML + fallback texto
    """

    try:
        from ecclesia.apps.users.models.user import User

        user = User.objects.get(pk=user_id)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verify_url = (f"{settings.BACKEND_URL}"f"/api/users/verify-email/"f"{uid}/"f"{token}")
        logger.info("Verification URL generated: %s", verify_url,)

        context = {
            "user_email": user.email,
            "verify_url":verify_url,
        }

        html_content = render_to_string("users/emails/verification_email.html", context,)
        text_content = strip_tags(html_content)     

        email = EmailMultiAlternatives(
            subject="Confirme seu e-mail — Ecclesia",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(html_content, "text/html",)

        email.send(fail_silently=False)

        logger.info("Verification email sent to %s", user.email,)

    except Exception as exc:

        logger.exception("Error sending verification email")

        raise self.retry(exc=exc)