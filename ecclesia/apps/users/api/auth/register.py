"""
Register endpoint — cadastro de usuários.
"""
from ninja import Router
from ecclesia.apps.users import services
from ecclesia.apps.users.schemas.users_schemas import (
    RegisterIn,
    TokenOut,
    MessageOut,
)
from ecclesia.apps.users.exceptions import UserAlreadyExists
from django_ratelimit.decorators import ratelimit
router = Router()


@router.post("/register", response={201: TokenOut, 409: MessageOut}, auth=None, summary="Cadastro de Igreja ou Membro",)
@ratelimit(key="ip", rate="5/h", block=True,)
def register(request, payload: RegisterIn):
    """
    Cria o usuário, o perfil (Church ou Member) e retorna tokens JWT.
    Um e-mail de verificação é enviado em background via Celery.
    """
    try:
        tokens = services.register_user(payload)
        return 201, tokens
    except UserAlreadyExists as e:
        return 409, {"detail": str(e)}