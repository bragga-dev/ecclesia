"""
Tasks Celery — convite de membro cadastrado por Igreja.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_member_invite_email(self, user_id: str, temp_password: str) -> None:
    """
    Envia e-mail de boas-vindas ao membro cadastrado pela Igreja.
    Inclui senha temporária e link de verificação de e-mail.
    """
    try:
        from dizimus.apps.users.models.user import User
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        user = User.objects.get(pk=user_id)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verify_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}/"

        logger.info("Member invite URL generated: %s", verify_url)

        text_message = (
            f"Olá, {user.email}!\n\n"
            "Você foi cadastrado em uma igreja na plataforma Ecclesia.\n\n"
            f"Sua senha temporária: {temp_password}\n\n"
            "Clique no link abaixo para confirmar seu e-mail e acessar sua conta:\n\n"
            f"{verify_url}\n\n"
            "Recomendamos que altere sua senha após o primeiro acesso.\n\n"
            "Se você não reconhece este cadastro, ignore esta mensagem."
        )

        html_message = f"""
        <html>
            <body style="font-family: sans-serif; max-width: 600px; margin: auto;">
                <h2>Bem-vindo à Ecclesia!</h2>

                <p>Olá, <strong>{user.email}</strong>!</p>

                <p>Você foi cadastrado em uma igreja na plataforma <strong>Ecclesia</strong>.</p>

                <p>Suas credenciais de acesso:</p>
                <ul>
                    <li><strong>E-mail:</strong> {user.email}</li>
                    <li><strong>Senha temporária:</strong> <code style="background:#f3f4f6; padding:2px 6px; border-radius:4px;">{temp_password}</code></li>
                </ul>

                <p>Clique no botão abaixo para confirmar seu e-mail:</p>

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

                <p>Ou copie este link:</p>
                <p>{verify_url}</p>

                <p style="color:#6b7280; font-size:0.875rem;">
                    Recomendamos que altere sua senha após o primeiro acesso.<br>
                    Se você não reconhece este cadastro, ignore esta mensagem.
                </p>
            </body>
        </html>
        """

        email = EmailMultiAlternatives(
            subject="Bem-vindo à Ecclesia — Confirme seu e-mail",
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)

        logger.info("Member invite email sent to %s", user.email)

    except Exception as exc:
        logger.exception("Error sending member invite email")
        raise self.retry(exc=exc)