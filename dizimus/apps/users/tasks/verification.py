"""
Tasks Celery — verificação de email.
"""

from celery import shared_task

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
        from dizimus.apps.users.models.user import User

        user = User.objects.get(pk=user_id)

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = default_token_generator.make_token(
            user
        )

        verify_url = (
            f"{settings.FRONTEND_URL}"
            f"/verify-email/"
            f"{uid}/"
            f"{token}/"
        )

        logger.info(
            "Verification URL generated: %s",
            verify_url,
        )

        text_message = (
            f"Olá, {user.email}!\n\n"
            "Clique no link abaixo para confirmar seu e-mail:\n\n"
            f"{verify_url}\n\n"
            "Se você não criou esta conta, ignore esta mensagem."
        )

        html_message = f"""
        <html>
            <body>

                <h2>Confirme seu e-mail</h2>

                <p>
                    Olá, {user.email}!
                </p>

                <p>
                    Clique no botão abaixo:
                </p>

                <p>
                    <a
                        href="{verify_url}"
                        style="
                            background:#2563eb;
                            color:white;
                            padding:12px 20px;
                            border-radius:8px;
                            text-decoration:none;
                            display:inline-block;
                        "
                    >
                        Confirmar e-mail
                    </a>
                </p>

                <p>
                    Ou copie este link:
                </p>

                <p>
                    {verify_url}
                </p>

            </body>
        </html>
        """

        email = EmailMultiAlternatives(
            subject="Confirme seu e-mail — Ecclesia",
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )

        email.attach_alternative(
            html_message,
            "text/html",
        )

        email.send(
            fail_silently=False
        )

        logger.info(
            "Verification email sent to %s",
            user.email,
        )

    except Exception as exc:

        logger.exception(
            "Error sending verification email"
        )

        raise self.retry(
            exc=exc
        )