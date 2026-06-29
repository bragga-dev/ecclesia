"""
Auth Services — autenticação, login, logout, refresh token.
"""
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from ecclesia.apps.users.models import User
from ecclesia.apps.users.exceptions import (
    InvalidCredentials,
    InvalidToken,
    InvalidPassword,
    EmailNotVerified,
)


def login_user(email: str, password: str) -> dict:
    user = authenticate(username=email, password=password)

    if not user:
        # Verifica se existe mas está inativo (email não confirmado)
        try:
            inactive_user = User.objects.get(email=email)
            if not inactive_user.is_active and inactive_user.check_password(password):
                raise EmailNotVerified()
        except User.DoesNotExist:
            pass
        raise InvalidCredentials()

    return _make_tokens(user)


def logout_user(refresh_token: str) -> None:
    """Blacklista o refresh token (requer ninja_jwt.token_blacklist)."""
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        raise InvalidToken()


def refresh_access_token(refresh_token: str) -> dict:
    try:
        token = RefreshToken(refresh_token)
        return {"access": str(token.access_token)}
    except Exception:
        raise InvalidToken()


def change_password(user: User, old_password: str, new_password: str) -> dict:
    """
    Troca a senha e invalida todos os refresh tokens ativos do usuário.
    Retorna um novo par de tokens para manter a sessão ativa.
    """
    if not user.check_password(old_password):
        raise InvalidPassword()

    user.set_password(new_password)
    user.save(update_fields=["password"])

    # Blacklista todos os refresh tokens ativos deste usuário
    outstanding = OutstandingToken.objects.filter(user=user)
    for token in outstanding:
        BlacklistedToken.objects.get_or_create(token=token)

    # Retorna novo par de tokens
    return _make_tokens(user)


def _make_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }