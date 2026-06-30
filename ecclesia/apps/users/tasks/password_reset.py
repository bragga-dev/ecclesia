"""
Tasks Celery — redefinição de senha.
"""
import logging
from celery import shared_task
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.utils.email_service import EmailService
from ecclesia.apps.users.utils.token_service import TokenService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id: str, uid: str, token: str) -> None:
    """
    Envia e-mail de redefinição de senha.
    - e-mail HTML + fallback texto
    """
    try:
        user = User.objects.get(pk=user_id)
        reset_url = TokenService.build_password_reset_url(uid, token)

        logger.info("Password reset URL generated: %s", reset_url)

        context = {
            "user_email": user.email,
            "reset_url": reset_url,
        }

        EmailService.send_html_email(
            subject="Redefinição de senha — Ecclesia",
            to_email=user.email,
            template_name="users/emails/password_reset.html",
            context=context,
        )

        logger.info("Password reset email sent to %s", user.email)

    except Exception as exc:
        logger.exception("Error sending password reset email")
        raise self.retry(exc=exc)