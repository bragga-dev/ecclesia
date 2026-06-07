"""
Tasks Celery — redefinição de senha.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_password_reset_email(self, user_id: str, uid: str, token: str) -> None:
    """
    Envia e-mail de redefinição de senha.
    - e-mail HTML + fallback texto
    """
    try:
        from dizimus.apps.users.models.user import User

        user = User.objects.get(pk=user_id)
        reset_url = f"{settings.FRONTEND_URL}/redefinir-senha/{uid}/{token}/"

        logger.info("Password reset URL generated: %s", reset_url)

        text_message = (
            f"Olá, {user.email}!\n\n"
            "Clique no link abaixo para redefinir sua senha:\n\n"
            f"{reset_url}\n\n"
            "O link expira em 1 hora. Se não foi você, ignore este e-mail."
        )

        html_message = f"""
        <html>
            <body>
                <h2>Redefinição de senha</h2>
                <p>
                    Olá, {user.email}!
                </p>
                <p>
                    Clique no botão abaixo para redefinir sua senha:
                </p>
                <p>
                    
                        href="{reset_url}"
                        style="
                            background:#2563eb;
                            color:white;
                            padding:12px 20px;
                            border-radius:8px;
                            text-decoration:none;
                            display:inline-block;
                        "
                    >
                        Redefinir senha
                    </a>
                </p>
                <p>
                    Ou copie este link:
                </p>
                <p>
                    {reset_url}
                </p>
                <p style="color:#6b7280; font-size:0.875rem;">
                    O link expira em 1 hora. Se não foi você, ignore este e-mail.
                </p>
            </body>
        </html>
        """

        email = EmailMultiAlternatives(
            subject="Redefinição de senha — Ecclesia",
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)

        logger.info("Password reset email sent to %s", user.email)

    except Exception as exc:
        logger.exception("Error sending password reset email")
        raise self.retry(exc=exc)