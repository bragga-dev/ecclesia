"""
Auth router — endpoints públicos de autenticação.
Registrado em config/api.py como: api.add_router("/auth/", ...)
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from dizimus.apps.users import services
from dizimus.apps.users.schemas.users_schemas import (
    RegisterIn,
    LoginIn,
    TokenOut,
    RefreshIn,
    ChangePasswordIn,
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    MessageOut,
)
from dizimus.apps.users.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    InvalidPassword,
    InvalidToken,
)

from dizimus.apps.users.api.verification import router as verification_router


router = Router()


# ── Registro ──────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response={201: TokenOut, 409: MessageOut},
    auth=None,                # rota pública
    summary="Cadastro de Igreja ou Membro",
)
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


# ── Login ─────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response={200: TokenOut, 401: MessageOut},
    auth=None,
    summary="Login",
)
def login(request, payload: LoginIn):
    try:
        tokens = services.login_user(payload.email, payload.password)
        return 200, tokens
    except InvalidCredentials as e:
        return 401, {"detail": str(e)}


# ── Refresh ───────────────────────────────────────────────────────────────────

@router.post(
    "/refresh",
    response={200: dict, 401: MessageOut},
    auth=None,
    summary="Renovar access token",
)
def refresh(request, payload: RefreshIn):
    try:
        data = services.refresh_access_token(payload.refresh)
        return 200, data
    except InvalidToken as e:
        return 401, {"detail": str(e)}


# ── Logout ────────────────────────────────────────────────────────────────────

@router.post(
    "/logout",
    response={200: MessageOut, 401: MessageOut},
    auth=JWTAuth(),
    summary="Logout (blacklista o refresh token)",
)
def logout(request, payload: RefreshIn):
    try:
        services.logout_user(payload.refresh)
        return 200, {"detail": "Logout realizado com sucesso."}
    except InvalidToken as e:
        return 401, {"detail": str(e)}


# ── Alterar senha ─────────────────────────────────────────────────────────────

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


# ── Reset de senha ────────────────────────────────────────────────────────────

@router.post("/password-reset/request", response={200: MessageOut}, auth=None, summary="Solicitar reset de senha",)
def password_reset_request(request, payload: PasswordResetRequestIn):
    services.request_password_reset(payload.email)
    return 200, {"detail": "Se este e-mail estiver cadastrado, você receberá as instruções em breve."}


@router.post("/password-reset/confirm", response={200: MessageOut, 400: MessageOut}, auth=None, summary="Confirmar reset de senha (nova versão)")
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




router.add_router("", verification_router)