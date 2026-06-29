"""
Login endpoint — autenticação de usuários.
"""
from ninja import Router
from ecclesia.apps.users import services
from ecclesia.apps.users.schemas.users_schemas import (
    LoginIn,
    TokenOut,
    MessageOut,
)
from ecclesia.apps.users.exceptions import InvalidCredentials, EmailNotVerified
from django_ratelimit.decorators import ratelimit

router = Router()

 

@router.post("/login", response={200: TokenOut, 401: MessageOut, 403: MessageOut}, auth=None, summary="Login")
@ratelimit(key="ip", rate="5/m", block=True)
def login(request, payload: LoginIn):
    try:
        tokens = services.login_user(payload.email, payload.password)
        return 200, tokens
    except EmailNotVerified:
        return 403, {"detail": "E-mail não verificado."}
    except InvalidCredentials:
        return 401, {"detail": "E-mail ou senha inválidos."}