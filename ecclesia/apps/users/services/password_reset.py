"""
Password Reset Services — solicitação e confirmação de redefinição de senha.
"""
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from ecclesia.apps.users.selectors import get_user_by_email
from ecclesia.apps.users.models import User
from ecclesia.apps.users import selectors
from ecclesia.apps.users.exceptions import InvalidToken


def request_password_reset(email: str) -> None:
    """
    Sempre retorna sem erro mesmo que o e-mail não exista
    (evita enumeração de usuários).
    """
    user = selectors.get_user_by_email(email)
    if not user:
        return

    from ecclesia.apps.users.tasks.password_reset import send_password_reset_email
    uid = urlsafe_base64_encode(force_bytes(user.pk)).rstrip("=")
    token = default_token_generator.make_token(user)
    send_password_reset_email.delay(user.pk, uid, token)


def confirm_password_reset(uidb64: str, token: str, new_password: str) -> None:
    try:
        padding = (4 - len(uidb64) % 4) % 4
        uid = force_str(urlsafe_base64_decode(uidb64 + "=" * padding))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        raise InvalidToken()

    if not default_token_generator.check_token(user, token):
        raise InvalidToken()

    user.set_password(new_password)
    user.save(update_fields=["password"])