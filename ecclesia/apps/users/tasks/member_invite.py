"""
Tasks Celery — convite de membro cadastrado por Igreja.
"""
import uuid
import logging
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_member_invite_email(self, user_id: str, temp_password: str, church_id: uuid.UUID) -> None:
    """
    Envia e-mail de boas-vindas ao membro cadastrado pela Igreja.
    Inclui senha temporária e link de verificação de e-mail.
    """
    try:
        from ecclesia.apps.users.models.user import User
        from ecclesia.apps.users.models.church import Church
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        user = User.objects.get(pk=user_id)
        church = Church.objects.get(id=church_id)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_url = f"{settings.BACKEND_URL}/api/users/verify-email/{uid}/{token}"

        

        logger.info("Member invite URL generated: %s", verify_url)
        context = {
        "member_email": user.email,
        "temp_password": temp_password,
        "verify_url": verify_url,
        "church_name": church.full_name,
        "member_email": user.email,
        "church_banner":church.banner_url,
        }

        html_content = render_to_string("users/emails/member_invite.html", context,)

        text_content = strip_tags(html_content) 

      
        
        email = EmailMultiAlternatives(
            subject="Bem-vindo à Ecclesia — Confirme seu e-mail",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        logger.info("Member invite email sent to %s", user.email)

    except Exception as exc:
        logger.exception("Error sending member invite email")
        raise self.retry(exc=exc)