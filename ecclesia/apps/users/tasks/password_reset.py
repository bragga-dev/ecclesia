"""
Tasks Celery — redefinição de senha.
"""
import logging
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from ecclesia.apps.users.models.user import User
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id: str, uid: str, token: str) -> None:
    """
    Envia e-mail de redefinição de senha.
    - e-mail HTML + fallback texto
    """
    try:
        

        user = User.objects.get(pk=user_id)
        reset_url = f"{settings.FRONTEND_URL}/redefinir-senha/{uid}/{token}"

        logger.info("Password reset URL generated: %s", reset_url)

        context = {           
            "user_email":user.email,
            "reset_url":reset_url,
        }

        html_content = render_to_string("users/emails/password_reset.html", context,)
        text_content = strip_tags(html_content)       

        email = EmailMultiAlternatives(
            subject="Redefinição de senha — Ecclesia",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info("Password reset email sent to %s", user.email)

    except Exception as exc:
        logger.exception("Error sending password reset email")
        raise self.retry(exc=exc)