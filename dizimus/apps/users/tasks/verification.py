"""
Tasks Celery — verificação de email.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_verification_email(self, user_id: str) -> None:
    from dizimus.apps.users.models.user import User
    try:
        user = User.objects.get(pk=user_id)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        verify_url = f"{settings.FRONTEND_URL}/verificar-email/{uid}/{token}/"

        send_mail(
            subject="Confirme seu e-mail — DIZIMUS",
            message=(
                f"Olá, {user.email}!\n\n"
                f"Clique no link para verificar seu e-mail:\n{verify_url}\n\n"
                "O link expira em 24 horas."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)