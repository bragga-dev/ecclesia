"""
Login endpoint — autenticação de usuários.
"""
from ninja import Router
from dizimus.apps.users import services
from dizimus.apps.users.schemas.users_schemas import (
    LoginIn,
    TokenOut,
    MessageOut,
)
from dizimus.apps.users.exceptions import InvalidCredentials
from django_ratelimit.decorators import ratelimit

router = Router()


@router.post("/login", response={200: TokenOut, 401: MessageOut},  auth=None, summary="Login",)
@ratelimit(key="ip", rate="5/m", block=True)
def login(request, payload: LoginIn):
    try:
        tokens = services.login_user(payload.email, payload.password)
        return 200, tokens
    except InvalidCredentials as e:
        return 401, {"detail": str(e)}