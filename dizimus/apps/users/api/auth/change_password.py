"""
Change Password endpoint — alteração de senha do usuário autenticado.
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from dizimus.apps.users import services
from dizimus.apps.users.schemas.users_schemas import (
    ChangePasswordIn,
    MessageOut,
)
from dizimus.apps.users.exceptions import InvalidPassword

router = Router()


@router.post(
    "/change-password",
    response={200: MessageOut, 400: MessageOut},
    auth=JWTAuth(),
    summary="Alterar senha",
)
def change_password(request, payload: ChangePasswordIn):
    try:
        services.change_password(
            user=request.auth,
            old_password=payload.old_password,
            new_password=payload.new_password,
        )
        return 200, {"detail": "Senha alterada com sucesso."}
    except InvalidPassword as e:
        return 400, {"detail": str(e)}