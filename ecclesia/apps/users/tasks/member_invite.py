"""
Tasks Celery — convite de membro cadastrado por Igreja.
"""
import uuid
import logging
from celery import shared_task
from ecclesia.apps.users.models.user import User
from ecclesia.apps.users.models.church import Church
from ecclesia.apps.users.utils.email_service import EmailService
from ecclesia.apps.users.utils.token_service import TokenService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_member_invite_email(self, user_id: str, temp_password: str, church_id: uuid.UUID) -> None:
    """
    Envia e-mail de boas-vindas ao membro cadastrado pela Igreja.
    Inclui senha temporária e link de verificação de e-mail.
    """
    try:
        user = User.objects.get(pk=user_id)
        church = Church.objects.get(id=church_id)

        uid, token = TokenService.generate_verification_data(user)
        verify_url = TokenService.build_verification_url(uid, token)

        logger.info("Member invite URL generated: %s", verify_url)

        context = {
            "member_email": user.email,  # Mantido como 'member_email' para compatibilidade com template
            "temp_password": temp_password,
            "verify_url": verify_url,
            "church_name": church.full_name,
            "church_banner": church.banner_url,
        }

        EmailService.send_html_email(
            subject="Bem-vindo à Ecclesia — Confirme seu e-mail",
            to_email=user.email,
            template_name="users/emails/member_invite.html",
            context=context,
        )

        logger.info("Member invite email sent to %s", user.email)

    except Exception as exc:
        logger.exception("Error sending member invite email")
        raise self.retry(exc=exc)