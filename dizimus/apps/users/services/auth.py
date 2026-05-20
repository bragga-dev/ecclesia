"""
Auth Services — autenticação, login, logout, refresh token.
"""
from django.contrib.auth import authenticate
from ninja_jwt.tokens import RefreshToken

from dizimus.apps.users.models import User
from dizimus.apps.users.exceptions import (
    InvalidCredentials,
    InvalidToken,
    InvalidPassword,
)


def login_user(email: str, password: str) -> dict:
    user = authenticate(username=email, password=password)
    if not user:
        raise InvalidCredentials()
    if not user.is_active:
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


def change_password(user: User, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise InvalidPassword()
    user.set_password(new_password)
    user.save(update_fields=["password"])


def _make_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }