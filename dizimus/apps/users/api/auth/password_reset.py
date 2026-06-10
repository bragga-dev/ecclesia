"""
Password Reset endpoints — solicitação e confirmação de reset de senha.
"""
from ninja import Router
from dizimus.apps.users import services
from dizimus.apps.users.schemas.users_schemas import (
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    MessageOut,
)
from dizimus.apps.users.exceptions import InvalidToken
from django_ratelimit.decorators import ratelimit

router = Router()


@router.post("/password-reset/request", response={200: MessageOut}, auth=None, summary="Solicitar reset de senha",)
@ratelimit(key="ip", rate="3/h", block=True,)
def password_reset_request(request, payload: PasswordResetRequestIn):
    services.request_password_reset(payload.email)
    return 200, {"detail": "Se este e-mail estiver cadastrado, você receberá as instruções em breve."}


@router.post("/password-reset/confirm", response={200: MessageOut, 400: MessageOut},  auth=None, summary="Confirmar reset de senha",)
@ratelimit(key="ip", rate="10/h",  block=True,)
def password_reset_confirm(request, payload: PasswordResetConfirmIn):
    try:
        services.confirm_password_reset(
            uidb64=payload.uid,
            token=payload.token,
            new_password=payload.new_password,
        )
        return 200, {"detail": "Senha redefinida com sucesso."}
    except InvalidToken:
        return 400, {"detail": "Token inválido ou expirado."}