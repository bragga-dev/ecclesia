# services/verification.py

from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from dizimus.apps.users.models import User
from dizimus.apps.users.exceptions import InvalidToken
from dizimus.apps.users.repositories import activate_user


def verify_email(uidb64: str, token: str) -> User:
    """
    Confirma o email do usuário usando uid e token.
    Retorna o usuário ativado ou levanta exceção.
    """

    try:
        uid = force_str(
            urlsafe_base64_decode(uidb64)
        )

        user = User.objects.get(pk=uid)

    except (
        User.DoesNotExist,
        ValueError,
        TypeError,
        OverflowError,
    ) as e:
        raise InvalidToken(
            f"Link inválido ou usuário não encontrado: {e}"
        )

    if not default_token_generator.check_token(user, token):
        raise InvalidToken(
            "Token inválido ou expirado."
        )

    return activate_user(user)