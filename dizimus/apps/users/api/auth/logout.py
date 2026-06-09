"""
Logout endpoint — blacklist do refresh token.
"""
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from dizimus.apps.users import services
from dizimus.apps.users.schemas.users_schemas import (
    RefreshIn,
    MessageOut,
)
from dizimus.apps.users.exceptions import InvalidToken
from django_ratelimit.decorators import ratelimit
router = Router()


@router.post("/logout", response={200: MessageOut, 401: MessageOut},  auth=JWTAuth(), summary="Logout (blacklista o refresh token)",)
@ratelimit(key="user", rate="30/m", block=True)
def logout(request, payload: RefreshIn):
    try:
        services.logout_user(payload.refresh)
        return 200, {"detail": "Logout realizado com sucesso."}
    except InvalidToken as e:
        return 401, {"detail": str(e)}