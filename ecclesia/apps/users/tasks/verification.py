"""
Tasks Celery — verificação de email.
"""
import logging
from celery import shared_task
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.utils.email_service import EmailService
from ecclesia.apps.users.utils.token_service import TokenService

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
        user = User.objects.get(pk=user_id)
        
        uid, token = TokenService.generate_verification_data(user)
        verify_url = TokenService.build_verification_url(uid, token)
        
        logger.info("Verification URL generated: %s", verify_url)

        context = {
            "user_email": user.email,
            "verify_url": verify_url,
        }

        EmailService.send_html_email(
            subject="Confirme seu e-mail — Ecclesia",
            to_email=user.email,
            template_name="users/emails/verification_email.html",
            context=context,
        )

        logger.info("Verification email sent to %s", user.email)

    except Exception as exc:
        logger.exception("Error sending verification email")
        raise self.retry(exc=exc)