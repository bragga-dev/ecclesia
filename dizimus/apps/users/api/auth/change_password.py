"""
Change Password endpoint — alteração de senha do usuário autenticado.
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from dizimus.apps.users import services
from dizimus.apps.users.schemas.users_schemas import (
    ChangePasswordIn,
    TokenOut,
    MessageOut,
)
from dizimus.apps.users.exceptions import InvalidPassword
from django_ratelimit.decorators import ratelimit

router = Router()


@router.post("/change-password",  response={200: TokenOut, 400: MessageOut, 429: MessageOut},
        auth=JWTAuth(), summary="Alterar senha", description=(
        "Troca a senha do usuário autenticado. "
        "Todos os tokens anteriores são invalidados e um novo par é retornado."
    ),
)
@ratelimit(key="user", rate="5/h", block=True)
def change_password(request, payload: ChangePasswordIn):
    try:
        tokens = services.change_password(
            user=request.auth,
            old_password=payload.old_password,
            new_password=payload.new_password,
        )
        return 200, tokens
    except InvalidPassword as e:
        return 400, {"detail": str(e)}